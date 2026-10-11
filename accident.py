import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from datetime import datetime

#plt.rcParams.update({'axes.facecolor': 'white', 'figure.facecolor': 'white'})

class AccidentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Accident Data Visualization System")
        self.root.geometry("1300x750")
        self.root.configure(bg="white")

        self.df = None

        title_label = tk.Label(root, text="Accident Data Visualization System",font=("Helvetica", 18, "bold"), bg="white", fg="#1a5276")
        title_label.pack(pady=10)

        control_frame = ttk.LabelFrame(root, text="Controls", padding=10)
        control_frame.pack(fill="x", padx=20, pady=10)

        ttk.Button(control_frame, text="Load CSV", command=self.load_csv).pack(side="left", padx=10)
        ttk.Button(control_frame, text="Generate Sample Data", command=self.generate_sample).pack(side="left", padx=10)

        ttk.Label(control_frame, text="Filter by Year:").pack(side="left", padx=5)
        self.year_cb = ttk.Combobox(control_frame, width=10, state="readonly")
        self.year_cb.pack(side="left", padx=5)
        self.year_cb.bind("<<ComboboxSelected>>", lambda e: self.update_charts())

        ttk.Label(control_frame, text="State:").pack(side="left", padx=5)
        self.state_cb = ttk.Combobox(control_frame, width=15, state="readonly")
        self.state_cb.pack(side="left", padx=5)
        self.state_cb.bind("<<ComboboxSelected>>", lambda e: self.update_city_options())

        ttk.Label(control_frame, text="City:").pack(side="left", padx=5)
        self.city_cb = ttk.Combobox(control_frame, width=15, state="readonly")
        self.city_cb.pack(side="left", padx=5)
        self.city_cb.bind("<<ComboboxSelected>>", lambda e: self.update_charts())

        chart_frame = tk.Frame(root, bg="white")
        chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

   
        self.bar_frame = ttk.LabelFrame(chart_frame, text="Vehicle Type Frequency (Bar Chart)")
        self.bar_frame.grid(row=0, column=0,sticky="nsew" ,padx=10, pady=10)

        self.line_frame = ttk.LabelFrame(chart_frame, text="Yearly Accident Trend (Line Chart)")
        self.line_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.pie_frame = ttk.LabelFrame(chart_frame, text="Top Accident-Prone Locations (Pie Chart)")
        self.pie_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        chart_frame.grid_rowconfigure(0, weight=1)
        chart_frame.grid_rowconfigure(1, weight=1)
        chart_frame.grid_columnconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(1, weight=1)

        self.fig_bar, self.ax_bar = plt.subplots(figsize=(5, 4))
        self.fig_line, self.ax_line = plt.subplots(figsize=(5, 4))
        self.fig_pie, self.ax_pie = plt.subplots(figsize=(6, 4))

        self.canvas_bar = FigureCanvasTkAgg(self.fig_bar, master=self.bar_frame)
        self.canvas_bar.get_tk_widget().pack(fill="both", expand=True)

        self.canvas_line = FigureCanvasTkAgg(self.fig_line, master=self.line_frame)
        self.canvas_line.get_tk_widget().pack(fill="both", expand=True)

        self.canvas_pie = FigureCanvasTkAgg(self.fig_pie, master=self.pie_frame)
        self.canvas_pie.get_tk_widget().pack(fill="both", expand=True)

   
    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        try:
            df = pd.read_csv(file_path)
            self.prepare_df(df)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {e}")


    def generate_sample(self):
        years = [2019, 2020, 2021, 2022, 2023, 2024]
        states = ["Karnataka", "Maharashtra", "Delhi"]
        cities = {
            "Karnataka": [("Bengaluru", 12.97, 77.59), ("Mysuru", 12.29, 76.64)],
            "Maharashtra": [("Mumbai", 19.07, 72.88), ("Pune", 18.52, 73.85), ("Nagpur", 21.15, 79.09)],
            "Delhi": [("Delhi", 28.61, 77.21)]
        }
        vehicle_types = ["Car", "Bike", "Truck", "Bus", "Auto"]

        records = []
        for i in range(200):
            state = random.choice(states)
            city, lat, lon = random.choice(cities[state])
            vehicle = random.choice(vehicle_types)
            year = random.choice(years)
            date = datetime(year, random.randint(1, 12), random.randint(1, 28))
            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "state": state,
                "city": city,
                "vehicle_type": vehicle,
                "latitude": lat + random.uniform(-0.05, 0.05),
                "longitude": lon + random.uniform(-0.05, 0.05)
            })

        df = pd.DataFrame(records)
        df.to_csv("accident_sample.csv", index=False)
        messagebox.showinfo("Sample Generated", "Sample dataset saved as accident_sample.csv")
        self.prepare_df(df)

   
    def prepare_df(self, df):
        df.columns = [c.lower().strip() for c in df.columns]
        if "date" not in df.columns:
            messagebox.showerror("Error", "CSV must contain a 'date' column")
            return

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["year"] = df["date"].dt.year
        self.df = df.dropna(subset=["year"])

        years = sorted(df["year"].dropna().unique())
        self.year_cb["values"] = ["All"] + [str(y) for y in years]
        self.year_cb.set("All")

        states = sorted(df["state"].dropna().unique())
        self.state_cb["values"] = ["All"] + states
        self.state_cb.set("All")

        self.update_city_options()

    def update_city_options(self):
        if self.df is None:
            return
        state = self.state_cb.get()
        if state == "All" or not state:
            cities = sorted(self.df["city"].dropna().unique())
        else:
            cities = sorted(self.df[self.df["state"] == state]["city"].dropna().unique())

        self.city_cb["values"] = ["All"] + cities
        self.city_cb.set("All")
        self.update_charts()

  
    def update_charts(self):
        if self.df is None:
            return

        df = self.df.copy()
        year = self.year_cb.get()
        state = self.state_cb.get()
        city = self.city_cb.get()

        if year != "All":
            df = df[df["year"] == int(year)]
        if state != "All":
            df = df[df["state"] == state]
        if city != "All":
            df = df[df["city"] == city]

     
        self.ax_bar.clear()
        freq = df["vehicle_type"].value_counts()
        self.ax_bar.bar(freq.index, freq.values, color="#5dade2")
        self.ax_bar.set_title("Vehicle Type Frequency")
        self.ax_bar.set_xlabel("Vehicle Type")
        self.ax_bar.set_ylabel("Number of Accidents")
        self.canvas_bar.draw()

      
        self.ax_line.clear()
        yearly = df.groupby("year").size()
        if not yearly.empty:
            self.ax_line.plot(yearly.index.to_numpy(), yearly.values, marker='o', color="#70ad47")
            self.ax_line.set_xlabel("Year")
            self.ax_line.set_ylabel("Number of Accidents")
            self.ax_line.set_title("Yearly Accident Trend")
        self.canvas_line.draw()

      
        self.ax_pie.clear()
        top_cities = df["city"].value_counts().head(5)
        if not top_cities.empty:
            self.ax_pie.pie(top_cities.values, labels=top_cities.index, autopct="%1.1f%%", colors=plt.cm.Paired.colors)
            self.ax_pie.set_title("Top Accident-Prone Locations")
        self.canvas_pie.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = AccidentGUI(root)
    root.mainloop()
