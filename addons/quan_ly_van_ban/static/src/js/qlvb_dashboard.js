/** @odoo-module **/

const { Component, useState } = owl;
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class QLVB_Dashboard extends Component {
  setup() {
    this.rpc = useService("rpc");
    this.state = useState({
      loading: true,
      summary: {
        totalVBDen: 0,
        totalVBDi: 0,
        totalQuaHan: 0,
        totalChoDuyet: 0,
        totalHopDong: 0,
        totalBaoGia: 0,
      },
      filters: {
        time_range: null,
      },
      data: {
        vbDenTrangThai: [],
        vbDiTrangThai: [],
        vbTheoNgay: { labels: [], den: [], di: [] },
      },
      recentVBDen: [],
      recentVBDi: [],
      vbQuaHan: [],
    });

    this.pieChart = null;
    this.lineChart = null;
  }

  async willStart() {
    await this.loadAll();
  }

  mounted() {
    this.renderCharts();
  }

  willUnmount() {
    if (this.pieChart) this.pieChart.destroy();
    if (this.lineChart) this.lineChart.destroy();
  }

  async loadAll() {
    this.state.loading = true;
    try {
      await this.loadSummary();
      await this.loadCharts();
      await this.loadTables();
      if (this.el) {
        this.renderCharts();
      }
    } catch (error) {
      console.error("Error loading dashboard:", error);
    } finally {
      this.state.loading = false;
    }
  }

  buildDateDomain(fieldName) {
    const domain = [];
    if (this.state.filters.time_range) {
      const days = Number(this.state.filters.time_range);
      if (days > 0) {
        const fromDate = new Date();
        fromDate.setDate(fromDate.getDate() - days);
        domain.push([fieldName, ">=", this.formatDate(fromDate)]);
      }
    }
    return domain;
  }

  async loadSummary() {
    try {
      // Tổng văn bản đến
      const totalVBDen = await this.rpc("/web/dataset/call_kw", {
        model: "van_ban_den",
        method: "search_count",
        args: [[]],
        kwargs: {},
      });

      // Tổng văn bản đi
      const totalVBDi = await this.rpc("/web/dataset/call_kw", {
        model: "van_ban_di",
        method: "search_count",
        args: [[]],
        kwargs: {},
      });

      // Văn bản quá hạn
      const today = this.formatDate(new Date());
      const totalQuaHan = await this.rpc("/web/dataset/call_kw", {
        model: "van_ban_den",
        method: "search_count",
        args: [
          [
            ["han_xu_ly", "<", today],
            ["trang_thai", "not in", ["da_xu_ly"]],
          ],
        ],
        kwargs: {},
      });

      // Văn bản chờ duyệt
      const totalChoDuyet = await this.rpc("/web/dataset/call_kw", {
        model: "van_ban_di",
        method: "search_count",
        args: [[["trang_thai", "=", "cho_duyet"]]],
        kwargs: {},
      });

      // Tổng hợp đồng
      const totalHopDong = await this.rpc("/web/dataset/call_kw", {
        model: "hop_dong",
        method: "search_count",
        args: [[]],
        kwargs: {},
      });

      // Tổng báo giá
      const totalBaoGia = await this.rpc("/web/dataset/call_kw", {
        model: "bao_gia",
        method: "search_count",
        args: [[]],
        kwargs: {},
      });

      this.state.summary.totalVBDen = totalVBDen || 0;
      this.state.summary.totalVBDi = totalVBDi || 0;
      this.state.summary.totalQuaHan = totalQuaHan || 0;
      this.state.summary.totalChoDuyet = totalChoDuyet || 0;
      this.state.summary.totalHopDong = totalHopDong || 0;
      this.state.summary.totalBaoGia = totalBaoGia || 0;
    } catch (error) {
      console.error("Error loading summary:", error);
    }
  }

  async loadCharts() {
    try {
      // Văn bản đến theo trạng thái
      const vbDenTT = await this.rpc("/web/dataset/call_kw", {
        model: "van_ban_den",
        method: "read_group",
        args: [[], ["trang_thai"], ["trang_thai"]],
        kwargs: {},
      });

      // Văn bản đi theo trạng thái
      const vbDiTT = await this.rpc("/web/dataset/call_kw", {
        model: "van_ban_di",
        method: "read_group",
        args: [[], ["trang_thai"], ["trang_thai"]],
        kwargs: {},
      });

      const denDateDomain = this.buildDateDomain("ngay_den");
      const diDateDomain = this.buildDateDomain("ngay_gui");

      // Văn bản đến theo ngày
      const vbDenNgay = await this.rpc("/web/dataset/call_kw", {
        model: "van_ban_den",
        method: "read_group",
        args: [denDateDomain, ["ngay_den"], ["ngay_den:day"]],
        kwargs: { orderby: "ngay_den" },
      });

      // Văn bản đi theo ngày
      const vbDiNgay = await this.rpc("/web/dataset/call_kw", {
        model: "van_ban_di",
        method: "read_group",
        args: [diDateDomain, ["ngay_gui"], ["ngay_gui:day"]],
        kwargs: { orderby: "ngay_gui" },
      });

      this.state.data.vbDenTrangThai = (vbDenTT || []).map((item) => ({
        label: this.mapTrangThaiVBDen(item.trang_thai),
        value: item.trang_thai_count || item.__count || 0,
      }));

      this.state.data.vbDiTrangThai = (vbDiTT || []).map((item) => ({
        label: this.mapTrangThaiVBDi(item.trang_thai),
        value: item.trang_thai_count || item.__count || 0,
      }));

      const denMap = new Map(
        (vbDenNgay || []).map((item) => [
          item["ngay_den:day"] || item.ngay_den || "",
          item.ngay_den_count || item.__count || 0,
        ]),
      );
      const diMap = new Map(
        (vbDiNgay || []).map((item) => [
          item["ngay_gui:day"] || item.ngay_gui || "",
          item.ngay_gui_count || item.__count || 0,
        ]),
      );

      const labels = Array.from(new Set([...denMap.keys(), ...diMap.keys()]))
        .filter((label) => label)
        .sort();

      this.state.data.vbTheoNgay = {
        labels,
        den: labels.map((label) => denMap.get(label) || 0),
        di: labels.map((label) => diMap.get(label) || 0),
      };
    } catch (error) {
      console.error("Error loading charts:", error);
    }
  }

  async loadTables() {
    try {
      const normalizeRecords = (res) => res?.records || res || [];

      // Văn bản đến gần nhất
      const recentVBDen = await this.rpc("/web/dataset/call_kw", {
        model: "van_ban_den",
        method: "search_read",
        args: [
          [],
          [
            "id",
            "so_ky_hieu",
            "trich_yeu",
            "noi_ban_hanh",
            "ngay_den",
            "trang_thai",
            "do_khan",
          ],
        ],
        kwargs: { order: "ngay_den desc", limit: 5 },
      });

      // Văn bản đi gần nhất
      const recentVBDi = await this.rpc("/web/dataset/call_kw", {
        model: "van_ban_di",
        method: "search_read",
        args: [
          [],
          [
            "id",
            "so_ky_hieu",
            "trich_yeu",
            "noi_nhan",
            "ngay_gui",
            "trang_thai",
          ],
        ],
        kwargs: { order: "ngay_gui desc", limit: 5 },
      });

      // Văn bản quá hạn
      const today = this.formatDate(new Date());
      const vbQuaHan = await this.rpc("/web/dataset/call_kw", {
        model: "van_ban_den",
        method: "search_read",
        args: [
          [
            ["han_xu_ly", "<", today],
            ["trang_thai", "not in", ["da_xu_ly"]],
          ],
          ["id", "so_ky_hieu", "trich_yeu", "han_xu_ly", "do_khan"],
        ],
        kwargs: { order: "han_xu_ly asc", limit: 5 },
      });

      this.state.recentVBDen = normalizeRecords(recentVBDen).map((rec) => ({
        id: rec.id,
        so_hieu: rec.so_ky_hieu || "-",
        trich_yeu: rec.trich_yeu || "-",
        noi_gui: rec.noi_ban_hanh || "-",
        ngay_den: rec.ngay_den || "-",
        trang_thai: this.mapTrangThaiVBDen(rec.trang_thai),
        do_khan: this.mapDoKhan(rec.do_khan),
      }));

      this.state.recentVBDi = normalizeRecords(recentVBDi).map((rec) => ({
        id: rec.id,
        so_hieu: rec.so_ky_hieu || "-",
        trich_yeu: rec.trich_yeu || "-",
        noi_nhan: rec.noi_nhan || "-",
        ngay_gui: rec.ngay_gui || "-",
        trang_thai: this.mapTrangThaiVBDi(rec.trang_thai),
      }));

      this.state.vbQuaHan = normalizeRecords(vbQuaHan).map((rec) => ({
        id: rec.id,
        so_hieu: rec.so_ky_hieu || "-",
        trich_yeu: rec.trich_yeu || "-",
        han_xu_ly: rec.han_xu_ly || "-",
        do_khan: this.mapDoKhan(rec.do_khan),
      }));
    } catch (error) {
      console.error("Error loading tables:", error);
    }
  }

  renderCharts() {
    if (!this.el) return;

    const pieCanvas = this.el.querySelector(".o_qlvb_pie_chart");
    const lineCanvas = this.el.querySelector(".o_qlvb_line_chart");

    if (!pieCanvas || !lineCanvas) return;

    const ChartLib = window.Chart;
    if (!ChartLib) return;

    if (this.pieChart) this.pieChart.destroy();
    if (this.lineChart) this.lineChart.destroy();

    const pieData = this.state.data.vbDenTrangThai || [];
    const lineData = this.state.data.vbTheoNgay || {
      labels: [],
      den: [],
      di: [],
    };

    this.pieChart = new ChartLib(pieCanvas.getContext("2d"), {
      type: "pie",
      data: {
        labels: pieData.map((d) => d.label),
        datasets: [
          {
            data: pieData.map((d) => d.value),
            backgroundColor: [
              "#60A5FA",
              "#34D399",
              "#FBBF24",
              "#F87171",
              "#A78BFA",
            ],
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          title: { display: true, text: "Văn bản đến theo trạng thái" },
          legend: { position: "bottom" },
        },
      },
    });

    this.lineChart = new ChartLib(lineCanvas.getContext("2d"), {
      type: "line",
      data: {
        labels: lineData.labels,
        datasets: [
          {
            label: "Văn bản đến",
            data: lineData.den,
            borderColor: "#3B82F6",
            backgroundColor: "rgba(59, 130, 246, 0.2)",
            fill: true,
            tension: 0.3,
          },
          {
            label: "Văn bản đi",
            data: lineData.di,
            borderColor: "#10B981",
            backgroundColor: "rgba(16, 185, 129, 0.2)",
            fill: true,
            tension: 0.3,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          title: { display: true, text: "Văn bản theo ngày" },
          legend: { display: true },
        },
        scales: {
          y: { beginAtZero: true },
        },
      },
    });
  }

  onTimeRangeChange(ev) {
    const val = parseInt(ev.target.value) || null;
    this.state.filters.time_range = val;
    this.loadAll();
  }

  formatDate(date) {
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, "0");
    const dd = String(date.getDate()).padStart(2, "0");
    return `${yyyy}-${mm}-${dd}`;
  }

  mapTrangThaiVBDen(value) {
    const map = {
      moi: "Mới",
      dang_xu_ly: "Đang xử lý",
      qua_han: "Quá hạn",
      da_xu_ly: "Đã xử lý",
      chuyen_tiep: "Chuyển tiếp",
    };
    return map[value] || "Khác";
  }

  mapTrangThaiVBDi(value) {
    const map = {
      du_thao: "Dự thảo",
      cho_duyet: "Chờ duyệt",
      da_duyet: "Đã duyệt",
      da_gui: "Đã gửi",
      hoan_tat: "Hoàn tất",
      huy: "Hủy",
    };
    return map[value] || "Khác";
  }

  mapDoKhan(value) {
    const map = {
      thuong: "Thường",
      khan: "Khẩn",
      hoa_toc: "Hỏa tốc",
      thuong_khat: "Thượng khẩn",
    };
    return map[value] || "Thường";
  }
}

QLVB_Dashboard.template = "quan_ly_van_ban.QLVBDashboard";
registry
  .category("actions")
  .add("quan_ly_van_ban.qlvb_dashboard", QLVB_Dashboard);
