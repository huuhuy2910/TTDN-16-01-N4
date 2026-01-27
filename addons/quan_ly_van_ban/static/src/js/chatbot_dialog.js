/** @odoo-module **/

const { Component } = owl;
const { useState, useRef, onMounted } = owl.hooks;

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class ChatbotDialog extends Component {
  setup() {
    this.rpc = useService("rpc");
    this.notification = useService("notification");
    this.actionService = useService("action");

    this.modelOptions = [
      { id: "openai_gpt4o_mini", label: "GPT-4o mini (OpenAI)" },
      { id: "gemini_pro", label: "Gemini 2.0 Flash (Google)" },
    ];

    this.state = useState({
      messages: [],
      inputValue: "",
      isLoading: false,
      isMinimized: false,
      selectedModel: this.modelOptions[0].id,
      uploadedFile: null,
      fileName: "",
      sessionId: null,
    });

    // Store file in a non-reactive property to avoid issues
    this.uploadedFileObject = null;

    this.inputRef = useRef("chatInput");
    this.messagesRef = useRef("chatMessages");
    this.fileInputRef = useRef("fileInput");

    this.suggestions = [
      "Văn bản nào đang quá hạn xử lý?",
      "Có bao nhiêu văn bản trong tháng này?",
    ];

    onMounted(async () => {
      if (this.inputRef.el) {
        this.inputRef.el.focus();
      }
      // Tạo session ID mới
      this.state.sessionId = this.generateSessionId();
    });
  }

  onInputKeydown(event) {
    // Chỉ cho phép xuống dòng với Shift+Enter, không gửi khi nhấn Enter
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      // Không gọi sendMessage() nữa - chỉ gửi khi nhấn nút
    }
  }

  useSuggestion(suggestion) {
    this.state.inputValue = suggestion;
    this.sendMessage();
  }

  closeDialog() {
    this.actionService.doAction({
      type: "ir.actions.act_window_close",
    });
  }

  toggleMinimize() {
    this.state.isMinimized = !this.state.isMinimized;
  }

  clearHistory() {
    this.state.messages = [];
  }

  generateSessionId() {
    return (
      "session_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9)
    );
  }

  toggleHistory() {
    this.actionService.doAction("quan_ly_van_ban.action_chat_history");
  }

  onModelChange(ev) {
    this.state.selectedModel = ev.target.value;
  }

  onFileSelect(event) {
    const file = event.target.files[0];
    if (!file) {
      return;
    }

    // Validate file is a proper File object
    if (!(file instanceof File)) {
      console.error("Selected object is not a File:", file);
      this.notification.add("Đối tượng file không hợp lệ.", {
        type: "danger",
      });
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      this.notification.add("File quá lớn. Kích thước tối đa là 10MB.", {
        type: "danger",
      });
      return;
    }

    // Validate file type
    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/bmp",
      "image/tiff",
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];
    if (!allowedTypes.includes(file.type)) {
      this.notification.add(
        "Định dạng file không được hỗ trợ. Chỉ chấp nhận: JPG, PNG, BMP, TIFF, PDF, DOCX.",
        {
          type: "danger",
        },
      );
      return;
    }

    // Store the actual File object in non-reactive property
    this.uploadedFileObject = file;
    this.state.uploadedFile = true; // Just a flag for UI
    this.state.fileName = file.name;

    console.log(
      "File selected:",
      file.name,
      file.type,
      file.size,
      "bytes",
      "File object:",
      file,
    );

    this.notification.add(`Đã chọn file: ${file.name}`, {
      type: "info",
    });
  }

  removeFile() {
    this.uploadedFileObject = null;
    this.state.uploadedFile = null;
    this.state.fileName = "";
    if (this.fileInputRef.el) {
      this.fileInputRef.el.value = "";
    }
  }

  async sendMessage() {
    const question = this.state.inputValue.trim();
    const hasFile = this.uploadedFileObject;

    if ((!question && !hasFile) || this.state.isLoading) return;

    // Add user message
    if (question) {
      this.state.messages.push({
        id: `tmp_${Date.now()}_${Math.random().toString(36).slice(2)}`,
        type: "user",
        content: question,
        time: this._formatTime(new Date()),
      });
    }

    if (hasFile) {
      this.state.messages.push({
        id: `tmp_${Date.now()}_${Math.random().toString(36).slice(2)}`,
        type: "user",
        content: `📎 Đã upload file: ${this.state.fileName}`,
        time: this._formatTime(new Date()),
      });
    }

    this.state.inputValue = "";
    this.state.isLoading = true;
    this._scrollToBottom();

    try {
      let result;

      if (hasFile) {
        // Use the stored file object
        const fileToUpload = this.uploadedFileObject;
        const fileName = this.state.fileName;

        // Validate file object
        if (!fileToUpload || !(fileToUpload instanceof File)) {
          throw new Error("File object không hợp lệ. Vui lòng chọn lại file.");
        }

        console.log(
          "Processing file upload:",
          fileName,
          fileToUpload.type,
          fileToUpload.size,
          "File object valid:",
          fileToUpload instanceof File,
        );

        // Process uploaded file
        const fileData = await this._readFileAsBase64(fileToUpload);

        console.log("File converted to base64, length:", fileData.length);

        result = await this.rpc("/chatbot/process_file", {
          file_data: fileData,
          file_name: fileName,
          model_key: this.state.selectedModel,
          question: question || "Hãy phân tích file này",
          session_id: this.state.sessionId,
        });

        // Clear uploaded file
        this.removeFile();
      } else {
        // Regular text query
        result = await this.rpc("/chatbot/ask", {
          question: question,
          model_key: this.state.selectedModel,
          session_id: this.state.sessionId,
        });
      }

      if (result.error) {
        this.state.messages.push({
          id: `tmp_${Date.now()}_${Math.random().toString(36).slice(2)}`,
          type: "error",
          content: `❌ **Lỗi:** ${result.error}`,
          time: this._formatTime(new Date()),
        });
        this.notification.add(result.error, {
          type: "danger",
        });
      } else if (!result.success && !result.answer && !result.response) {
        this.state.messages.push({
          id: `tmp_${Date.now()}_${Math.random().toString(36).slice(2)}`,
          type: "error",
          content: "❌ **Lỗi:** Không nhận được phản hồi từ server.",
          time: this._formatTime(new Date()),
        });
      } else {
        let responseContent =
          result.answer || result.response || "Không có phản hồi";

        if (result.extracted_text) {
          responseContent = `📄 **Nội dung trích xuất:**\n${result.extracted_text}\n\n📝 **Tóm tắt:**\n${result.summary || responseContent}`;
        }

        this.state.messages.push({
          id: `tmp_${Date.now()}_${Math.random().toString(36).slice(2)}`,
          type: "bot",
          content: responseContent,
          time: this._formatTime(new Date()),
        });
      }
    } catch (error) {
      console.error("Chatbot error:", error);

      let errorMessage = "Không thể kết nối đến server. ";

      if (error.message) {
        errorMessage += `Chi tiết: ${error.message}`;
      } else {
        errorMessage += "Vui lòng kiểm tra:\n";
        errorMessage += "• Kết nối internet\n";
        errorMessage += "• Server Odoo đang chạy\n";
        errorMessage += "• API key đã được cấu hình trong file .env";
      }

      this.state.messages.push({
        type: "error",
        content: `❌ **Lỗi kết nối:**\n${errorMessage}`,
        time: this._formatTime(new Date()),
      });

      this.notification.add("Không thể kết nối đến server chatbot", {
        type: "danger",
      });
    } finally {
      this.state.isLoading = false;
      this._scrollToBottom();
    }
  }

  _readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
      console.log("_readFileAsBase64 called with:", file);
      console.log("File type check - instanceof File:", file instanceof File);
      console.log("File type check - instanceof Blob:", file instanceof Blob);
      console.log("File properties:", {
        name: file.name,
        size: file.size,
        type: file.type,
        lastModified: file.lastModified,
      });

      // Validate file is actually a Blob/File object
      if (!file || !(file instanceof Blob)) {
        console.error("File validation failed:", file);
        reject(new Error("Invalid file object - not a Blob or File"));
        return;
      }

      const reader = new FileReader();
      reader.onload = () => {
        console.log(
          "FileReader onload called, result length:",
          reader.result.length,
        );
        resolve(reader.result.split(",")[1]); // Remove data:image/... prefix
      };
      reader.onerror = (error) => {
        console.error("FileReader error:", error);
        reject(error);
      };
      reader.readAsDataURL(file);
    });
  }

  _formatTime(date) {
    return date.toLocaleTimeString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  _scrollToBottom() {
    setTimeout(() => {
      if (this.messagesRef.el) {
        this.messagesRef.el.scrollTop = this.messagesRef.el.scrollHeight;
      }
    }, 100);
  }
}

ChatbotDialog.template = "quan_ly_van_ban.ChatbotDialog";
ChatbotDialog.components = {};

// Đăng ký client action
registry.category("actions").add("open_chatbot_dialog", ChatbotDialog);
