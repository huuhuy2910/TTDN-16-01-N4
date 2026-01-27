# -*- coding: utf-8 -*-
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ChatbotController(http.Controller):
    """Controller cho AI trợ lý nội bộ."""

    @http.route('/qlvb/chatbot/models', type='json', auth='user', methods=['GET'], csrf=False)
    def get_available_models(self, **kwargs):
        """
        Endpoint trả về danh sách models AI có sẵn.
        
        Response:
            {"success": true, "models": [{"id": "...", "label": "...", "provider": "..."}]}
        """
        try:
            chatbot_service = request.env['chatbot.service'].sudo()
            models = []
            for key, config in chatbot_service.SUPPORTED_MODELS.items():
                models.append({
                    'id': key,
                    'label': config['label'],
                    'provider': config['provider'],
                })
            return {'success': True, 'models': models}
        except Exception as e:
            _logger.exception("Get models error: %s", str(e))
            return {'success': False, 'error': str(e)}

    @http.route('/chatbot/ask', type='json', auth='user', methods=['POST'], csrf=False)
    def chatbot_ask(self, question=None, model_key=None, session_id=None, **kwargs):
        """
        Endpoint nhận câu hỏi từ chatbot và trả về câu trả lời.
        
        Request body:
            {"jsonrpc": "2.0", "method": "call", "params": {"question": "...", "session_id": "..."}}
        
        Response:
            {"success": true, "answer": "..."} hoặc
            {"success": false, "error": "..."}
        """
        _logger.info("Chatbot ask called with question: %s, model: %s, session: %s", question, model_key, session_id)
        
        if not question:
            return {'success': False, 'error': 'Vui lòng nhập câu hỏi.'}
        
        # Kiểm tra quyền người dùng (có thể mở rộng theo nhóm)
        user = request.env.user
        if not user or user._is_public():
            return {'success': False, 'error': 'Bạn cần đăng nhập để sử dụng chatbot.'}
        
        # Gọi service xử lý
        try:
            chatbot_service = request.env['chatbot.service'].sudo()
            result = chatbot_service.ask(
                question,
                model_key=model_key,
                session_id=session_id,
                user_id=user.id,
            )
            _logger.info("Chatbot response success: %s", result.get('success', False))
            return result
        except Exception as e:
            _logger.exception("Chatbot controller error: %s", str(e))
            return {'success': False, 'error': f'Lỗi hệ thống: {str(e)}'}

    @http.route('/chatbot/process_file', type='json', auth='user', methods=['POST'], csrf=False)
    def process_uploaded_file(self, file_data=None, file_name=None, model_key=None, question=None, session_id=None, **kwargs):
        """
        Endpoint xử lý file upload từ chatbot.
        
        Request body:
            {
                "file_data": "base64_string",
                "file_name": "filename.ext", 
                "model_key": "openai_gpt4o_mini",
                "question": "optional question about the file",
                "session_id": "session_id"
            }
        
        Response:
            {"success": true, "extracted_text": "...", "summary": "..."} hoặc
            {"error": "..."}
        """
        if not file_data or not file_name:
            return {'error': 'Thiếu dữ liệu file hoặc tên file.'}
        
        # Kiểm tra quyền người dùng
        user = request.env.user
        if not user or user._is_public():
            return {'error': 'Bạn cần đăng nhập để sử dụng chatbot.'}
        
        try:
            chatbot_service = request.env['chatbot.service'].sudo()
            result = chatbot_service.process_uploaded_file(
                file_data,
                file_name,
                model_key,
                question,
                session_id,
                user_id=user.id,
            )
            
            if result.get('success'):
                return result
            else:
                return {'error': result.get('error', 'Lỗi xử lý file không xác định.')}
                
        except Exception as e:
            _logger.exception("File processing error: %s", str(e))
            return {'error': f'Lỗi hệ thống: {str(e)}'}
