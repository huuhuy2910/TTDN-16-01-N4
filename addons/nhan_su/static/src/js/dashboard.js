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
      filters: {
        don_vi: null,
        chuc_vu: null,
      },
      filterOptions: {
        donVi: [],
        chucVu: [],
      },
      loading: true,
    });

    this.pieChart = null;
    this.barChart = null;
  }

  async willStart() {
    await super.willStart();
    await this.loadFilterOptions();
    await this.loadData();
  }

  mounted() {
    super.mounted();
    this.renderCharts();
  }

  async loadFilterOptions() {
    try {
      const donViResult = await this.rpc("/web/dataset/search_read", {
        model: "don_vi",
        fields: ["id", "ten_don_vi"],
        limit: 100,
      });
      const chucVuResult = await this.rpc("/web/dataset/search_read", {
        model: "chuc_vu",
        fields: ["id", "ten_chuc_vu"],
        limit: 100,
      });

      this.state.filterOptions.donVi = donViResult.records;
      this.state.filterOptions.chucVu = chucVuResult.records;
    } catch (error) {
      console.error("Error loading filter options:", error);
    }
  }

  async loadData() {
    this.state.loading = true;
    try {
      // Đếm theo bảng lich_su_cong_tac để tránh phụ thuộc field compute chưa được tính
      const domain = this.buildDomain();

      const result = await this.rpc("/web/dataset/call_kw", {
        model: "lich_su_cong_tac",
        method: "read_group",
        args: [domain, ["don_vi_id"], ["don_vi_id"]],
        kwargs: { limit: 200 },
      });
      console.debug("Dashboard don_vi read_group result", result);

      const donViData = result.map((item) => ({
        label: item.don_vi_id ? item.don_vi_id[1] : "Chưa xác định",
        value: item.__count ?? 0,
      }));

      const chucVuResult = await this.rpc("/web/dataset/call_kw", {
        model: "lich_su_cong_tac",
        method: "read_group",
        args: [domain, ["chuc_vu_id"], ["chuc_vu_id"]],
        kwargs: { limit: 200 },
      });
      console.debug("Dashboard chuc_vu read_group result", chucVuResult);

      const nhanSuData = chucVuResult.map((item) => ({
        label: item.chuc_vu_id ? item.chuc_vu_id[1] : "Chưa xác định",
        value: item.__count ?? 0,
      }));

      console.debug("Dashboard mapped data", {
        donViDataLength: donViData.length,
        nhanSuDataLength: nhanSuData.length,
        donViData,
        nhanSuData,
      });

      this.state.data.donViData = donViData;
      this.state.data.nhanSuData = nhanSuData;

      // Chỉ render khi component đã mount (this.el tồn tại)
      if (this.el) {
        this.renderCharts();
      } else {
        // fallback an toàn: thử render sau 0ms khi el sẵn sàng
        setTimeout(() => {
          if (this.el) {
            this.renderCharts();
          }
        }, 0);
      }
    } catch (error) {
      console.error("Error loading dashboard data:", error);
    } finally {
      this.state.loading = false;
    }
  }

  buildDomain() {
    const domain = [];
    if (this.state.filters.don_vi) {
      domain.push(["don_vi_id", "=", this.state.filters.don_vi]);
    }
    if (this.state.filters.chuc_vu) {
      domain.push(["chuc_vu_id", "=", this.state.filters.chuc_vu]);
    }
    return domain;
  }

  renderCharts() {
    // Nếu chưa mount, bỏ qua
    if (!this.el) {
      return;
    }

    if (this.pieChart) {
      this.pieChart.destroy();
    }
    if (this.barChart) {
      this.barChart.destroy();
    }

    const ChartLib = window.Chart;
    if (!ChartLib) {
      console.warn("Chart.js not loaded; dashboard charts will not render.");
      return;
    }

    const pieCanvas = this.el.querySelector("canvas[name='pieChart']");
    const barCanvas = this.el.querySelector("canvas[name='barChart']");

    if (!pieCanvas || !barCanvas) {
      console.warn("Canvas elements not found");
      return;
    }

    const pieCtx = pieCanvas.getContext("2d");
    this.pieChart = new ChartLib(pieCtx, {
      type: "pie",
      data: {
        labels: this.state.data.donViData.map((d) => d.label),
        datasets: [
          {
            data: this.state.data.donViData.map((d) => d.value),
            backgroundColor: [
              "#FF6384",
              "#36A2EB",
              "#FFCE56",
              "#4BC0C0",
              "#9966FF",
              "#FF9F40",
            ],
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: "bottom",
          },
          title: {
            display: true,
            text: "Nhân viên theo phòng ban",
          },
        },
      },
    });

    const barCtx = barCanvas.getContext("2d");
    this.barChart = new ChartLib(barCtx, {
      type: "bar",
      data: {
        labels: this.state.data.nhanSuData.map((d) => d.label),
        datasets: [
          {
            label: "Số nhân viên",
            data: this.state.data.nhanSuData.map((d) => d.value),
            backgroundColor: "#36A2EB",
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false,
          },
          title: {
            display: true,
            text: "Nhân viên theo chức vụ",
          },
        },
        scales: {
          y: {
            beginAtZero: true,
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

  onFilterChange(field, value) {
    this.state.filters[field] = value;
    this.loadData();
  }
}

NhanSuDashboard.template = "nhan_su.Dashboard";

console.log("Registering nhan_su.dashboard action...");
registry.category("actions").add("nhan_su.dashboard", NhanSuDashboard);
console.log("nhan_su.dashboard action registered successfully!");
