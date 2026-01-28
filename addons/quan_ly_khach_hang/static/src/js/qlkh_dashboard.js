/** @odoo-module **/

const { Component, useState } = owl;
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class QLKH_Dashboard extends Component {
  setup() {
    this.rpc = useService("rpc");
    this.state = useState({
      loading: true,
      summary: {
        totalKhachHang: 0,
        totalHopDong: 0,
        totalDoanhThu: 0,
        totalCongNo: 0,
        totalCoHoi: 0,
        totalKhieuNai: 0,
      },
      filters: {
        time_range: null,
        nhan_vien: null,
      },
      filterOptions: {
        nhanVien: [],
      },
      data: {
        khachHangLoai: [],
        hopDongTrangThai: [],
        doanhThuThang: [],
      },
      recentCoHoi: [],
      sapHetHan: [],
      alerts: [],
    });

    this.pieChart = null;
    this.lineChart = null;
    this.barChart = null;
  }

  async willStart() {
    await this.loadFilterOptions();
    await this.loadAll();
  }

  mounted() {
    this.renderCharts();
  }

  willUnmount() {
    if (this.pieChart) this.pieChart.destroy();
    if (this.lineChart) this.lineChart.destroy();
    if (this.barChart) this.barChart.destroy();
  }

  async loadFilterOptions() {
    try {
      const nhanVienResult = await this.rpc("/web/dataset/search_read", {
        model: "nhan_vien",
        fields: ["id", "ho_va_ten"],
        limit: 200,
      });
      this.state.filterOptions.nhanVien = nhanVienResult.records || [];
    } catch (error) {
      console.error("Error loading filter options:", error);
    }
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

  buildNhanVienDomain(fieldName) {
    const domain = [];
    if (this.state.filters.nhan_vien) {
      domain.push([fieldName, "=", this.state.filters.nhan_vien]);
    }
    return domain;
  }

  async loadSummary() {
    try {
      // Không dùng filter, lấy tất cả để đảm bảo có dữ liệu
      const totalKhachHang = await this.rpc("/web/dataset/call_kw", {
        model: "khach_hang",
        method: "search_count",
        args: [[]],
        kwargs: {},
      });

      const totalHopDong = await this.rpc("/web/dataset/call_kw", {
        model: "hop_dong",
        method: "search_count",
        args: [[]],
        kwargs: {},
      });

      const totalCoHoi = await this.rpc("/web/dataset/call_kw", {
        model: "co_hoi_ban_hang",
        method: "search_count",
        args: [[]],
        kwargs: {},
      });

      // Tổng doanh thu từ hóa đơn đã thanh toán
      const tongDoanhThuGroup = await this.rpc("/web/dataset/call_kw", {
        model: "hoa_don",
        method: "read_group",
        args: [
          [["trang_thai", "=", "da_thanh_toan"]],
          ["tong_thanh_toan:sum"],
          [],
        ],
        kwargs: {},
      });
      const totalDoanhThu =
        (tongDoanhThuGroup &&
          tongDoanhThuGroup[0] &&
          tongDoanhThuGroup[0].tong_thanh_toan) ||
        0;

      // Tổng công nợ
      const congNoGroup = await this.rpc("/web/dataset/call_kw", {
        model: "hoa_don",
        method: "read_group",
        args: [[["con_no", ">", 0]], ["con_no:sum"], []],
        kwargs: {},
      });
      const totalCongNo =
        (congNoGroup && congNoGroup[0] && congNoGroup[0].con_no) || 0;

      // Khiếu nại đang xử lý
      const totalKhieuNai = await this.rpc("/web/dataset/call_kw", {
        model: "khieu_nai_phan_hoi",
        method: "search_count",
        args: [[["trang_thai", "in", ["moi", "dang_xu_ly", "cho_phan_hoi"]]]],
        kwargs: {},
      });

      this.state.summary.totalKhachHang = totalKhachHang || 0;
      this.state.summary.totalHopDong = totalHopDong || 0;
      this.state.summary.totalCoHoi = totalCoHoi || 0;
      this.state.summary.totalDoanhThu = totalDoanhThu || 0;
      this.state.summary.totalCongNo = totalCongNo || 0;
      this.state.summary.totalKhieuNai = totalKhieuNai || 0;
    } catch (error) {
      console.error("Error loading summary:", error);
    }
  }

  async loadCharts() {
    try {
      // Phân loại khách hàng
      const khLoai = await this.rpc("/web/dataset/call_kw", {
        model: "khach_hang",
        method: "read_group",
        args: [[], ["loai_khach_hang"], ["loai_khach_hang"]],
        kwargs: {},
      });

      // Trạng thái hợp đồng
      const hopDongTT = await this.rpc("/web/dataset/call_kw", {
        model: "hop_dong",
        method: "read_group",
        args: [[], ["trang_thai"], ["trang_thai"]],
        kwargs: {},
      });

      // Doanh thu theo tháng
      const doanhThuThang = await this.rpc("/web/dataset/call_kw", {
        model: "hoa_don",
        method: "read_group",
        args: [
          [["trang_thai", "=", "da_thanh_toan"]],
          ["tong_thanh_toan:sum"],
          ["ngay_xuat:month"],
        ],
        kwargs: { orderby: "ngay_xuat" },
      });

      this.state.data.khachHangLoai = (khLoai || []).map((item) => ({
        label: this.mapLoaiKhachHang(item.loai_khach_hang),
        value: item.loai_khach_hang_count || item.__count || 0,
      }));

      this.state.data.hopDongTrangThai = (hopDongTT || []).map((item) => ({
        label: this.mapTrangThaiHopDong(item.trang_thai),
        value: item.trang_thai_count || item.__count || 0,
      }));

      this.state.data.doanhThuThang = (doanhThuThang || []).map((item) => ({
        label: item["ngay_xuat:month"] || item.ngay_xuat || "",
        value: item.tong_thanh_toan || 0,
      }));
    } catch (error) {
      console.error("Error loading charts:", error);
    }
  }

  async loadTables() {
    try {
      // Lấy cơ hội mới nhất
      const recentCoHoi = await this.rpc("/web/dataset/search_read", {
        model: "co_hoi_ban_hang",
        domain: [],
        fields: [
          "id",
          "ten_co_hoi",
          "khach_hang_id",
          "gia_tri_du_kien",
          "giai_doan",
          "ty_le_thanh_cong",
          "ngay_tao",
        ],
        order: "ngay_tao desc",
        limit: 8,
      });

      // Hợp đồng sắp hết hạn (30 ngày tới)
      const today = new Date();
      const next30 = new Date();
      next30.setDate(today.getDate() + 30);
      const hopDongDomain = [
        ["ngay_het_han", ">=", this.formatDate(today)],
        ["ngay_het_han", "<=", this.formatDate(next30)],
        ["trang_thai", "=", "hieu_luc"],
      ];

      const sapHetHan = await this.rpc("/web/dataset/search_read", {
        model: "hop_dong",
        domain: hopDongDomain,
        fields: [
          "id",
          "ma_hop_dong",
          "ten_hop_dong",
          "khach_hang_id",
          "ngay_het_han",
        ],
        order: "ngay_het_han asc",
        limit: 8,
      });

      this.state.recentCoHoi = (recentCoHoi.records || []).map((rec) => ({
        id: rec.id,
        ten_co_hoi: rec.ten_co_hoi,
        khach_hang: rec.khach_hang_id ? rec.khach_hang_id[1] : "-",
        gia_tri_du_kien: rec.gia_tri_du_kien || 0,
        giai_doan: this.mapGiaiDoan(rec.giai_doan),
        ty_le: rec.ty_le_thanh_cong || 0,
        ngay_tao: rec.ngay_tao || "-",
      }));

      this.state.sapHetHan = (sapHetHan.records || []).map((rec) => ({
        id: rec.id,
        ma: rec.ma_hop_dong || "-",
        ten: rec.ten_hop_dong || "-",
        khach_hang: rec.khach_hang_id ? rec.khach_hang_id[1] : "-",
        ngay_het_han: rec.ngay_het_han || "-",
      }));
    } catch (error) {
      console.error("Error loading tables:", error);
    }
  }

  renderCharts() {
    if (!this.el) return;

    const pieCanvas = this.el.querySelector(".o_qlkh_pie_chart");
    const lineCanvas = this.el.querySelector(".o_qlkh_line_chart");
    if (!pieCanvas || !lineCanvas) return;

    const ChartLib = window.Chart;
    if (!ChartLib) return;

    if (this.pieChart) this.pieChart.destroy();
    if (this.lineChart) this.lineChart.destroy();
    const pieData = this.state.data.hopDongTrangThai || [];
    const lineData = this.state.data.doanhThuThang || [];

    this.pieChart = new ChartLib(pieCanvas.getContext("2d"), {
      type: "pie",
      data: {
        labels: pieData.map((d) => d.label),
        datasets: [
          {
            data: pieData.map((d) => d.value),
            backgroundColor: [
              "#F97316",
              "#FB7185",
              "#A78BFA",
              "#22C55E",
              "#38BDF8",
            ],
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          title: { display: true, text: "Hợp đồng theo trạng thái" },
          legend: { position: "bottom" },
        },
      },
    });

    this.lineChart = new ChartLib(lineCanvas.getContext("2d"), {
      type: "line",
      data: {
        labels: lineData.map((d) => d.label),
        datasets: [
          {
            label: "Doanh thu",
            data: lineData.map((d) => d.value),
            borderColor: "#3B82F6",
            backgroundColor: "rgba(59, 130, 246, 0.2)",
            fill: true,
            tension: 0.3,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          title: { display: true, text: "Doanh thu theo tháng" },
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

  onNhanVienChange(ev) {
    const val = parseInt(ev.target.value) || null;
    this.state.filters.nhan_vien = val;
    this.loadAll();
  }

  formatDate(date) {
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, "0");
    const dd = String(date.getDate()).padStart(2, "0");
    return `${yyyy}-${mm}-${dd}`;
  }

  mapLoaiKhachHang(value) {
    const map = {
      ca_nhan: "Cá nhân",
      doanh_nghiep: "Doanh nghiệp",
    };
    return map[value] || "Khác";
  }

  mapTrangThaiHopDong(value) {
    const map = {
      nhap: "Nháp",
      cho_duyet: "Chờ duyệt",
      hieu_luc: "Hiệu lực",
      het_han: "Hết hạn",
      huy: "Đã hủy",
    };
    return map[value] || "Khác";
  }

  mapGiaiDoan(value) {
    const map = {
      moi: "Mới",
      du_dieu_kien: "Đủ điều kiện",
      bao_gia: "Báo giá",
      dam_phan: "Đàm phán",
      thang: "Thắng",
      thua: "Thua",
    };
    return map[value] || "Khác";
  }

  formatCurrency(value) {
    try {
      return new Intl.NumberFormat("vi-VN", {
        style: "currency",
        currency: "VND",
      }).format(value);
    } catch (e) {
      return value;
    }
  }
}

QLKH_Dashboard.template = "quan_ly_khach_hang.Dashboard";
registry
  .category("actions")
  .add("quan_ly_khach_hang.dashboard", QLKH_Dashboard);
