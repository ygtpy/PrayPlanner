import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import sv_ttk  # Modern tema için
from ttkthemes import ThemedTk  # Ek temalar için
from PIL import Image, ImageTk
import os
from win10toast import ToastNotifier

def get_prayer_times():
    iframe_url = "https://m.dinimizislam.com/NamazVakti_HP/namazvakti.asp?ff=Arial&fs=16"
    try:
        response = requests.get(iframe_url)
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
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Hata", f"Bağlantı hatası: {e}")
        return {}

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

class App(ThemedTk):  # tk.Tk yerine ThemedTk kullanıyoruz
    def __init__(self):
        super().__init__()
        
        self.toaster = ToastNotifier()

        # Tema ayarları
        self.set_theme("arc")  # Modern flat tema
        sv_ttk.set_theme("light")  # Sun Valley teması
        
        self.title("Namaz Vakitleri ve Günlük Program")
        self.geometry("1200x800")
        self.configure(bg='#f0f0f0')  # Açık gri arka plan
        
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
        self.create_widgets()
        
        # İlk programı oluştur
        self.update_program()
        
        # Otomatik güncelleme
        self.after(1800000, self.auto_update)

    def create_widgets(self):
        # Sol panel - Namaz vakitleri
        left_panel = ttk.Frame(self.main_container, style="Card.TFrame")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
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
            prayer_card.grid_columnconfigure(1, weight=1)  # Orta sütunu esnek yap
            
            icon_label = ttk.Label(prayer_card, text=prayer_icons[prayer], 
                                 font=("Segoe UI", 18), style="Prayer.TLabel",
                                 width=3)  # Sabit genişlik
            icon_label.grid(row=0, column=0, padx=5)
            
            name_label = ttk.Label(prayer_card, text=f"{prayer}:", 
                                 font=("Segoe UI", 12),
                                 style="Prayer.TLabel",
                                 width=8)  # Sabit genişlik
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
                                style="Title.TLabel")
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

    def update_program(self):
        prayer_times = get_prayer_times()
        
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
        update_time = datetime.now().strftime("%H:%M")
        self.toaster.show_toast(
            "Program Güncellendi",
            f"Namaz vakitleri ve program {update_time}'de güncellendi.",
            duration=5,
            threaded=True  # Bildirim ana programı bloklamasın
    )

    def auto_update(self):
        self.update_program()
        self.after(1800000, self.auto_update)

if __name__ == "__main__":
    app = App()
    # app.mainloop()