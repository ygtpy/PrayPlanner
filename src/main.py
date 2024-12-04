import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import sv_ttk
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import os
from win10toast import ToastNotifier
import json

def add_minutes(time_str, minutes):
    time = datetime.strptime(time_str, "%H:%M")
    new_time = time + timedelta(minutes=minutes)
    return new_time.strftime("%H:%M")

def subtract_minutes(time_str, minutes):
    time = datetime.strptime(time_str, "%H:%M")
    new_time = time - timedelta(minutes=minutes)
    return new_time.strftime("%H:%M")

def update_schedule(prayer_times):
    # Sabit süreli etkinlikler için buffer süreleri
    PRAYER_BUFFER_BEFORE = 15  # Namaz öncesi hazırlık süresi
    PRAYER_DURATION = {
        'Sabah': 25,
        'Öğle': 20,
        'İkindi': 20,
        'Akşam': 25,
        'Yatsı': 25
    }
    
    schedule = []
    
    # Sabah rutini
    if 'Sabah' in prayer_times:
        sabah_time = datetime.strptime(prayer_times['Sabah'], "%H:%M")
        wakeup_time = (sabah_time - timedelta(minutes=120)).strftime("%H:%M")  # Sabah namazından 2 saat önce
        
        schedule.extend([
            (wakeup_time, "Uyanış"),
            (f"{wakeup_time} - {add_minutes(wakeup_time, 30)}", "Abdest ve Teheccüd namazı"),
            (f"{add_minutes(wakeup_time, 30)} - {add_minutes(wakeup_time, 60)}", "Kitap okuma (30 dk)"),
            (f"{add_minutes(wakeup_time, 60)} - {subtract_minutes(prayer_times['Sabah'], PRAYER_BUFFER_BEFORE)}", "Kuran okuma ve zikir"),
            (f"{subtract_minutes(prayer_times['Sabah'], PRAYER_BUFFER_BEFORE)} - {add_minutes(prayer_times['Sabah'], PRAYER_DURATION['Sabah'])}", "Sabah namazı"),
        ])
        
        work_start = add_minutes(prayer_times['Sabah'], PRAYER_DURATION['Sabah'])
        
        # Sabah namazı sonrası 
        schedule.extend([
            (f"{work_start} - {add_minutes(work_start, 60)}", "İngilizce çalışma (1 saat)"),
            (f"{add_minutes(work_start, 60)} - {add_minutes(work_start, 120)}", "Kahvaltı ve hazırlık"),
            (f"{add_minutes(work_start, 120)} - 10:30", "1. Yazılım projesi çalışması"),
            ("10:30 - 11:00", "Kısa mola ve hafif atıştırmalık")
        ])
    
    # Öğle 
    if 'Öğle' in prayer_times:
        ogle_start = subtract_minutes(prayer_times['Öğle'], PRAYER_BUFFER_BEFORE)
        schedule.extend([
            (f"11:00 - {ogle_start}", "2. Yazılım projesi çalışması"),
            (f"{ogle_start} - {add_minutes(prayer_times['Öğle'], PRAYER_DURATION['Öğle'])}", "Öğle namazı"),
            (f"{add_minutes(prayer_times['Öğle'], PRAYER_DURATION['Öğle'])} - {add_minutes(prayer_times['Öğle'], 60)}", "Öğle yemeği"),
            (f"{add_minutes(prayer_times['Öğle'], 60)} - {add_minutes(prayer_times['Öğle'], 120)}", "Dinlenme ve kısa uyku")
        ])
        
        work_restart = add_minutes(prayer_times['Öğle'], 120)
    
    # İkindi 
    if 'İkindi' in prayer_times:
        ikindi_start = subtract_minutes(prayer_times['İkindi'], PRAYER_BUFFER_BEFORE)
        schedule.extend([
            (f"{work_restart} - {ikindi_start}", "3. Yazılım projesi çalışması"),
            (f"{ikindi_start} - {add_minutes(prayer_times['İkindi'], PRAYER_DURATION['İkindi'])}", "İkindi namazı"),
            (f"{add_minutes(prayer_times['İkindi'], PRAYER_DURATION['İkindi'])} - {subtract_minutes(prayer_times['Akşam'], 60)}", "Yeni teknolojiler öğrenme")
        ])
    
    # Akşam 
    if 'Akşam' in prayer_times:
        aksam_start = subtract_minutes(prayer_times['Akşam'], PRAYER_BUFFER_BEFORE)
        schedule.extend([
            (f"{subtract_minutes(prayer_times['Akşam'], 60)} - {aksam_start}", "Spor/Yürüyüş"),
            (f"{aksam_start} - {add_minutes(prayer_times['Akşam'], PRAYER_DURATION['Akşam'])}", "Akşam namazı")
        ])
    
    # Yatsı ve gece 
    if 'Yatsı' in prayer_times:
        yatsi_start = subtract_minutes(prayer_times['Yatsı'], PRAYER_BUFFER_BEFORE)
        schedule.extend([
            (f"{add_minutes(prayer_times['Akşam'], PRAYER_DURATION['Akşam'])} - {yatsi_start}", "Akşam yemeği ve aile zamanı"),
            (f"{yatsi_start} - {add_minutes(prayer_times['Yatsı'], PRAYER_DURATION['Yatsı'])}", "Yatsı namazı"),
            (f"{add_minutes(prayer_times['Yatsı'], PRAYER_DURATION['Yatsı'])} - 22:00", "Aile ile sohbet / Sosyal medya kontrolü"),
            ("22:00 - 22:30", "Kitap okuma (30 dk)"),
            ("22:30 - 23:00", "Ertesi gün planlaması ve hazırlık"),
            ("23:00", "Yatış")
        ])
    
    return schedule

class App(ThemedTk):
    def __init__(self):
        super().__init__()
        
        # Şehir verilerini saklamak için dictionary
        self.cities = {}
        
        # Config dosyası yolu
        self.config_file = "app_config.json"
        
        self.toaster = ToastNotifier()

        # Tema ayarları
        self.set_theme("arc")
        sv_ttk.set_theme("light")
        
        self.title("PrayPlanner V2.0.1")
        self.geometry("1200x800")
        self.configure(bg='#f0f0f0')
        
        # Stil ayarları
        self.style = ttk.Style()
        self.style.configure("Card.TFrame", background="#ffffff", relief="flat")
        self.style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), background="#ffffff")
        self.style.configure("Prayer.TLabel", font=("Segoe UI", 12), background="#ffffff", padding=10)
        self.style.configure("Current.TLabel", background="#e3f2fd", font=("Segoe UI", 12, "bold"))
        
        # Ana container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Grid yapısı için ağırlıklar
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=3)

        self.prayer_labels = {}
        self.schedule = []
        
        # Şehir listesini yükle
        self.load_cities()
        
        # Widget'ları oluştur
        self.create_widgets()
        
        # Kayıtlı şehri yükle ve uygula
        self.load_saved_city()
        
        # İlk programı oluştur
        self.update_program()
        
        # Otomatik güncelleme
        self.after(1800000, self.auto_update)

    def load_cities(self):
        try:
            url = "https://m.dinimizislam.com/NamazVakti_HP/namazvakti.asp"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/100.0'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            select = soup.find('select', {'name': 'id'})
            if select:
                options = select.find_all('option')
                if options:
                    for option in options:
                        city_name = option.text.strip()
                        city_id = option['value']
                        self.cities[city_name] = city_id
                else:
                    raise Exception("Şehir listesi boş!")
            else:
                raise Exception("Şehir seçim listesi bulunamadı!")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Şehir listesi yüklenirken hata oluştu: {str(e)}")
            self.cities = {"İstanbul": "17300"}  # Varsayılan şehir

    def create_widgets(self):
        # Sol panel - Namaz vakitleri
        left_panel = ttk.Frame(self.main_container, style="Card.TFrame")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Şehir seçimi için frame
        city_frame = ttk.Frame(left_panel, style="Card.TFrame")
        city_frame.pack(fill="x", padx=10, pady=5)
        
        city_label = ttk.Label(city_frame, text="Şehir Seçin:", 
                             font=("Segoe UI", 10), style="Prayer.TLabel")
        city_label.pack(side="left", padx=5)
        
        # Şehir seçimi için Combobox
        self.city_combobox = ttk.Combobox(city_frame, 
                                         values=list(self.cities.keys()),
                                         state="readonly",
                                         font=("Segoe UI", 10))
        self.city_combobox.pack(side="left", fill="x", expand=True, padx=5)
        self.city_combobox.bind('<<ComboboxSelected>>', self.on_city_select)
        
        # Başlık ve tarih
        header_frame = ttk.Frame(left_panel, style="Card.TFrame")
        header_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = ttk.Label(header_frame, text="Namaz Vakitleri", style="Title.TLabel")
        title_label.pack(side="top", pady=5)
        
        date_label = ttk.Label(header_frame, 
                             text=f"{datetime.now().strftime('%d %B %Y %A')}", 
                             font=("Segoe UI", 10))
        date_label.pack(side="top")
        
        # Namaz vakitleri kartları
        prayer_frame = ttk.Frame(left_panel, style="Card.TFrame")
        prayer_frame.pack(fill="x", padx=10, pady=10)
        
        prayer_icons = {
            'Sabah': '🌅',
            'Öğle': '🌞',
            'İkindi': '🌤️',
            'Akşam': '🌅',
            'Yatsı': '🌙'
        }
        
        # Grid sistemi kullanarak düzenli hizalama
        for i, prayer in enumerate(['Sabah', 'Öğle', 'İkindi', 'Akşam', 'Yatsı']):
            prayer_card = ttk.Frame(prayer_frame, style="Card.TFrame")
            prayer_card.pack(fill="x", pady=5)
            
            # Grid ile yerleşim
            prayer_card.grid_columnconfigure(1, weight=1)
            
            icon_label = ttk.Label(prayer_card, text=prayer_icons[prayer], 
                                 font=("Segoe UI", 18), style="Prayer.TLabel",
                                 width=3)
            icon_label.grid(row=0, column=0, padx=5)
            
            name_label = ttk.Label(prayer_card, text=f"{prayer}:", 
                                 font=("Segoe UI", 12),
                                 style="Prayer.TLabel",
                                 width=8)
            name_label.grid(row=0, column=1, padx=5, sticky="w")
            
            time_label = ttk.Label(prayer_card, text="--:--",
                                 font=("Segoe UI", 12), 
                                 style="Prayer.TLabel")
            time_label.grid(row=0, column=2, padx=10, sticky="e")
            
            self.prayer_labels[prayer] = time_label
        
        # Güncelleme butonu
        update_btn = ttk.Button(left_panel, text="Programı Güncelle", 
                              command=self.update_program, 
                              style="Accent.TButton")
        update_btn.pack(pady=20)
        
        # Sağ panel - Program tablosu
        right_panel = ttk.Frame(self.main_container, style="Card.TFrame")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Program başlığı
        program_title = ttk.Label(right_panel, text="Günlük Programım", 
                                style="Title.TLabel",font=("nsew",15))
        program_title.pack(pady=10)
        
        # Tablo container
        table_container = ttk.Frame(right_panel)
        table_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_container)
        scrollbar.pack(side="right", fill="y")
        
        # Program tablosu
        self.schedule_tree = ttk.Treeview(table_container, 
                                        columns=("Saat", "Aktivite"),
                                        show="headings",
                                        style="Custom.Treeview")
        
        # Tablo stilleri
        self.style.configure("Custom.Treeview",
                           background="#ffffff",
                           fieldbackground="#ffffff",
                           rowheight=30,
                           font=("Segoe UI", 10))
        
        self.style.configure("Custom.Treeview.Heading",
                           font=("Segoe UI", 11, "bold"))
        
        # Tablo başlıkları
        self.schedule_tree.heading("Saat", text="Saat")
        self.schedule_tree.heading("Aktivite", text="Aktivite")
        
        # Sütun genişlikleri
        self.schedule_tree.column("Saat", width=150, minwidth=150)
        self.schedule_tree.column("Aktivite", width=400, minwidth=300)
        
        self.schedule_tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar bağlantısı
        scrollbar.config(command=self.schedule_tree.yview)
        self.schedule_tree.config(yscrollcommand=scrollbar.set)
        
        # Tablo satır renkleri
        self.schedule_tree.tag_configure('current', 
                                       background='#e3f2fd',
                                       font=("Segoe UI", 10, "bold"))
        self.schedule_tree.tag_configure('even', background='#fafafa')
        self.schedule_tree.tag_configure('odd', background='#ffffff')

    def load_saved_city(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    saved_city = config.get('selected_city', None)
                    if saved_city and saved_city in self.cities:
                        self.city_combobox.set(saved_city)
                    else:
                        # Varsayılan şehri seç
                        self.city_combobox.set(list(self.cities.keys())[0])
            else:
                # Varsayılan şehri seç
                self.city_combobox.set(list(self.cities.keys())[0])
        except Exception as e:
            messagebox.showerror("Hata", f"Kayıtlı şehir yüklenirken hata oluştu: {str(e)}")
            self.city_combobox.set(list(self.cities.keys())[0])

    def save_selected_city(self, city):
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config['selected_city'] = city
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Hata", f"Şehir kaydedilirken hata oluştu: {str(e)}")

    def on_city_select(self, event=None):
        selected_city = self.city_combobox.get()
        self.save_selected_city(selected_city)
        self.update_program()

    def get_prayer_times(self):
        selected_city = self.city_combobox.get()
        
        if not selected_city or selected_city not in self.cities:
            messagebox.showerror("Hata", "Lütfen geçerli bir şehir seçin!")
            return {}
            
        try:
            city_id = self.cities[selected_city]
            url = "https://m.dinimizislam.com/NamazVakti_HP/namazvakti.asp"
            params = {
                'id': city_id,
                'ff': 'Arial',
                'fs': '16'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/100.0'
            }
            
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            prayer_times = {}
            table = soup.find('table', class_='table table-sm table-striped mb-0')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) == 2:
                        name = cells[0].text.strip()
                        time = cells[1].text.strip()
                        if name in ['Sabah', 'Öğle', 'İkindi', 'Akşam', 'Yatsı']:
                            prayer_times[name] = time
            
            return prayer_times
            
        except Exception as e:
            messagebox.showerror("Hata", f"Namaz vakitleri alınırken hata oluştu: {str(e)}")
            return {}

    def update_program(self):
        prayer_times = self.get_prayer_times()
        
        if not prayer_times:
            messagebox.showwarning("Uyarı", 
                                 "Namaz vakitleri alınamadı. "
                                 "Lütfen internet bağlantınızı kontrol edin.",
                                 parent=self)
            return
            
        # Namaz vakitlerini güncelle
        for prayer, time in prayer_times.items():
            if prayer in self.prayer_labels:
                self.prayer_labels[prayer].config(text=time)

        # Günlük programı güncelle
        self.schedule = update_schedule(prayer_times)
        
        # Treeview'ı temizle
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)
        
        # Yeni programı ekle
        current_time = datetime.now().time()
        for i, (time_range, activity) in enumerate(self.schedule):
            tags = []
            if i % 2 == 0:
                tags.append('even')
            else:
                tags.append('odd')
                
            if ' - ' in time_range:
                start_time = datetime.strptime(time_range.split(' - ')[0], 
                                             "%H:%M").time()
                end_time = datetime.strptime(time_range.split(' - ')[1], 
                                           "%H:%M").time()
                if start_time <= current_time <= end_time:
                    tags.append('current')
            
            self.schedule_tree.insert("", "end", 
                                    values=(time_range, activity), 
                                    tags=tags)

        selected_city = self.city_combobox.get()
        update_time = datetime.now().strftime("%H:%M")
        self.toaster.show_toast(
            "Program Güncellendi",
            f"{selected_city} için namaz vakitleri ve program {update_time}'de güncellendi.",
            duration=5,
            threaded=True
        )

    def auto_update(self):
        self.update_program()
        self.after(1800000, self.auto_update)  # 30 dakikada bir güncelle

if __name__ == "__main__":
    app = App()
    app.mainloop()