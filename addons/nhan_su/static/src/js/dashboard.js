/** @odoo-module **/

const { Component, useState } = owl;
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class NhanSuDashboard extends Component {
  setup() {
    this.rpc = useService("rpc");
    this.state = useState({
      data: {
        donViData: [],
        nhanSuData: [],
      },
      summary: {
        totalNhanVien: 0,
        totalDonVi: 0,
        totalQuanLy: 0,
      },
      recentNhanVien: [],
      filters: {
        don_vi: null,
        chuc_vu: null,
        time_range: null,
      },
      filterOptions: {
        donVi: [],
        chucVu: [],
      },
      loading: true,
    });

    this.pieChart = null;
    this.barChart = null;
    this.deptBarChart = null;
  }

  async willStart() {
    await this.loadFilterOptions();
    await this.loadData();
  }

  mounted() {
    this.renderCharts();
  }

  willUnmount() {
    if (this.pieChart) {
      this.pieChart.destroy();
      this.pieChart = null;
    }
    if (this.barChart) {
      this.barChart.destroy();
      this.barChart = null;
    }
    if (this.deptBarChart) {
      this.deptBarChart.destroy();
      this.deptBarChart = null;
    }
  }

  async loadFilterOptions() {
    try {
      const donViResult = await this.rpc("/web/dataset/search_read", {
        model: "don_vi",
        fields: ["id", "ten_don_vi"],
        limit: 200,
      });
      const chucVuResult = await this.rpc("/web/dataset/search_read", {
        model: "chuc_vu",
        fields: ["id", "ten_chuc_vu"],
        limit: 200,
      });

      this.state.filterOptions.donVi = donViResult.records || [];
      this.state.filterOptions.chucVu = chucVuResult.records || [];
    } catch (error) {
      console.error("Error loading filter options:", error);
    }
  }

  async loadData() {
    this.state.loading = true;
    try {
      const domain = await this.buildDomain();

      const records = await this.rpc("/web/dataset/search_read", {
        model: "lich_su_cong_tac",
        domain,
        fields: ["don_vi_id", "chuc_vu_id"],
        limit: 10000,
      });
      console.debug("Dashboard lich_su_cong_tac search_read result", records);

      const donViCount = {};
      const chucVuCount = {};

      (records.records || []).forEach((rec) => {
        const donViLabel = rec.don_vi_id ? rec.don_vi_id[1] : "Chưa xác định";
        const chucVuLabel = rec.chuc_vu_id
          ? rec.chuc_vu_id[1]
          : "Chưa xác định";

        donViCount[donViLabel] = (donViCount[donViLabel] || 0) + 1;
        chucVuCount[chucVuLabel] = (chucVuCount[chucVuLabel] || 0) + 1;
      });

      const donViData = Object.entries(donViCount).map(([label, value]) => ({
        label,
        value: Number(value) || 0,
      }));

      const nhanSuData = Object.entries(chucVuCount).map(([label, value]) => ({
        label,
        value: Number(value) || 0,
      }));

      console.debug("Dashboard mapped data", {
        donViDataLength: donViData.length,
        nhanSuDataLength: nhanSuData.length,
        donViData,
        nhanSuData,
      });

      this.state.data.donViData = donViData;
      this.state.data.nhanSuData = nhanSuData;

      await this.loadSummary(domain, donViData);
      await this.loadRecentNhanVien();

      // Render charts nếu đã mounted
      if (this.el) {
        this.renderCharts();
      }
    } catch (error) {
      console.error("Error loading dashboard data:", error);
    } finally {
      this.state.loading = false;
    }
  }

  async buildDomain() {
    const domain = [];
    if (this.state.filters.don_vi) {
      domain.push(["don_vi_id", "=", this.state.filters.don_vi]);
    }
    if (this.state.filters.chuc_vu) {
      domain.push(["chuc_vu_id", "=", this.state.filters.chuc_vu]);
    }

    const nhanVienDomain = this.buildNhanVienDomain();
    if (nhanVienDomain.length > 0) {
      const idsResult = await this.rpc("/web/dataset/search_read", {
        model: "nhan_vien",
        domain: nhanVienDomain,
        fields: ["id"],
        limit: 5000,
      });
      const ids = (idsResult.records || []).map((r) => r.id);
      if (ids.length > 0) {
        domain.push(["nhan_vien_id", "in", ids]);
      } else {
        domain.push(["id", "=", 0]);
      }
    }
    return domain;
  }

  buildNhanVienDomain() {
    const domain = [];
    if (this.state.filters.don_vi) {
      domain.push(["don_vi_hien_tai", "=", this.state.filters.don_vi]);
    }
    if (this.state.filters.chuc_vu) {
      domain.push(["chuc_vu_hien_tai", "=", this.state.filters.chuc_vu]);
    }
    if (this.state.filters.time_range) {
      const days = Number(this.state.filters.time_range);
      if (days > 0) {
        const fromDate = new Date();
        fromDate.setDate(fromDate.getDate() - days);
        domain.push(["create_date", ">=", this.formatDate(fromDate)]);
      }
    }
    return domain;
  }

  async loadSummary(domain, donViData) {
    try {
      const totalDonViRaw = await this.rpc("/web/dataset/call_kw", {
        model: "don_vi",
        method: "search_count",
        args: [[]],
        kwargs: {},
      });

      const totalNhanVienRaw = await this.rpc("/web/dataset/call_kw", {
        model: "nhan_vien",
        method: "search_count",
        args: [[]],
        kwargs: {},
      });

      let totalNhanVien = totalNhanVienRaw || 0;
      if (!totalNhanVien) {
        const nvGroups = await this.rpc("/web/dataset/call_kw", {
          model: "lich_su_cong_tac",
          method: "read_group",
          args: [[], ["nhan_vien_id"], ["nhan_vien_id"]],
          kwargs: { limit: 100000 },
        });
        totalNhanVien = (nvGroups || []).length;
      }

      const chucVuQuanLy = await this.rpc("/web/dataset/search_read", {
        model: "chuc_vu",
        domain: [
          ["cap_do", ">=", 1],
          ["cap_do", "<=", 4],
        ],
        fields: ["id"],
        limit: 500,
      });
      const quanLyIds = (chucVuQuanLy.records || []).map((r) => r.id);

      let totalQuanLy = 0;
      if (quanLyIds.length > 0) {
        totalQuanLy = await this.rpc("/web/dataset/call_kw", {
          model: "nhan_vien",
          method: "search_count",
          args: [[["chuc_vu_hien_tai", "in", quanLyIds]]],
          kwargs: {},
        });
        if (!totalQuanLy) {
          const quanLyGroups = await this.rpc("/web/dataset/call_kw", {
            model: "lich_su_cong_tac",
            method: "read_group",
            args: [
              ["chuc_vu_id", "in", quanLyIds],
              ["nhan_vien_id"],
              ["nhan_vien_id"],
            ],
            kwargs: { limit: 100000 },
          });
          totalQuanLy = (quanLyGroups || []).length;
        }
      }

      const totalDonVi = totalDonViRaw || (donViData ? donViData.length : 0);

      this.state.summary.totalNhanVien = totalNhanVien || 0;
      this.state.summary.totalDonVi = totalDonVi || 0;
      this.state.summary.totalQuanLy = totalQuanLy || 0;
    } catch (error) {
      console.error("Error loading summary:", error);
    }
  }

  async loadRecentNhanVien() {
    try {
      const nhanVienDomain = this.buildNhanVienDomain();
      const result = await this.rpc("/web/dataset/search_read", {
        model: "nhan_vien",
        domain: nhanVienDomain,
        fields: [
          "id",
          "ho_va_ten",
          "don_vi_hien_tai",
          "chuc_vu_hien_tai",
          "create_date",
        ],
        order: "create_date desc",
        limit: 9,
      });

      this.state.recentNhanVien = (result.records || []).map((rec) => ({
        id: rec.id,
        ho_va_ten: rec.ho_va_ten || "",
        don_vi_hien_tai: rec.don_vi_hien_tai ? rec.don_vi_hien_tai[1] : "-",
        chuc_vu_hien_tai: rec.chuc_vu_hien_tai ? rec.chuc_vu_hien_tai[1] : "-",
        ngay_vao: rec.create_date ? rec.create_date.split(" ")[0] : "-",
      }));
    } catch (error) {
      console.error("Error loading recent employees:", error);
    }
  }

  renderCharts() {
    if (!this.el) {
      return;
    }

    const pieCanvas = this.el.querySelector(".o_nhan_su_pie_chart");
    const barCanvas = this.el.querySelector(".o_nhan_su_bar_chart");
    const deptBarCanvas = this.el.querySelector(".o_nhan_su_dept_bar_chart");

    if (!pieCanvas || !barCanvas || !deptBarCanvas) {
      console.warn("Canvas elements not found");
      return;
    }

    if (this.pieChart) {
      this.pieChart.destroy();
    }
    if (this.barChart) {
      this.barChart.destroy();
    }
    if (this.deptBarChart) {
      this.deptBarChart.destroy();
    }

    const ChartLib = window.Chart;
    if (!ChartLib) {
      console.warn("Chart.js not loaded; dashboard charts will not render.");
      return;
    }

    // Kiểm tra dữ liệu
    const donViData = this.state.data.donViData || [];
    const nhanSuData = this.state.data.nhanSuData || [];

    console.log("Rendering charts with data:", { donViData, nhanSuData });

    const pieCtx = pieCanvas.getContext("2d");
    this.pieChart = new ChartLib(pieCtx, {
      type: "pie",
      data: {
        labels: donViData.map((d) => d.label),
        datasets: [
          {
            data: donViData.map((d) => d.value),
            backgroundColor: [
              "#FF6384",
              "#36A2EB",
              "#FFCE56",
              "#4BC0C0",
              "#9966FF",
              "#FF9F40",
              "#E7E9ED",
              "#8B5CF6",
            ],
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: "bottom",
            display: donViData.length > 0,
          },
          title: {
            display: true,
            text:
              donViData.length > 0
                ? "Nhân viên theo phòng ban"
                : "Chưa có dữ liệu phòng ban",
          },
        },
      },
    });

    const barCtx = barCanvas.getContext("2d");
    this.barChart = new ChartLib(barCtx, {
      type: "line",
      data: {
        labels: nhanSuData.map((d) => d.label),
        datasets: [
          {
            label: "Số nhân viên",
            data: nhanSuData.map((d) => d.value),
            borderColor: "#36A2EB",
            backgroundColor: "rgba(54, 162, 235, 0.2)",
            fill: true,
            tension: 0.3,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            display: true,
          },
          title: {
            display: true,
            text:
              nhanSuData.length > 0
                ? "Nhân viên theo chức vụ"
                : "Chưa có dữ liệu chức vụ",
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              precision: 0,
            },
          },
        },
      },
    });

    const deptBarCtx = deptBarCanvas.getContext("2d");
    this.deptBarChart = new ChartLib(deptBarCtx, {
      type: "bar",
      data: {
        labels: donViData.map((d) => d.label),
        datasets: [
          {
            label: "Số nhân viên",
            data: donViData.map((d) => d.value),
            backgroundColor: "rgba(255, 159, 64, 0.6)",
            borderColor: "rgba(255, 159, 64, 1)",
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            display: true,
          },
          title: {
            display: true,
            text:
              donViData.length > 0
                ? "Số nhân viên theo phòng ban"
                : "Chưa có dữ liệu phòng ban",
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1,
              precision: 0,
            },
          },
        },
      },
    });
  }

  onDonViChange(ev) {
    const val = parseInt(ev.target.value) || null;
    this.onFilterChange("don_vi", val);
  }

  onChucVuChange(ev) {
    const val = parseInt(ev.target.value) || null;
    this.onFilterChange("chuc_vu", val);
  }

  onTimeRangeChange(ev) {
    const val = parseInt(ev.target.value) || null;
    this.onFilterChange("time_range", val);
  }

  onFilterChange(field, value) {
    this.state.filters[field] = value;
    this.loadData();
  }

  formatDate(date) {
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, "0");
    const dd = String(date.getDate()).padStart(2, "0");
    return `${yyyy}-${mm}-${dd}`;
  }
}

NhanSuDashboard.template = "nhan_su.Dashboard";

console.log("Registering nhan_su.dashboard action...");
registry.category("actions").add("nhan_su.dashboard", NhanSuDashboard);
console.log("nhan_su.dashboard action registered successfully!");
