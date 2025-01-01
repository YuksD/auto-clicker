from models.automation_model import AutomationModel
from utils.constants import Constants
import keyboard
import time
import threading

class AutomationViewModel:
    def __init__(self):
        self.model = AutomationModel()
        self.constants = Constants()
        
        # Callback'ler
        self.on_state_changed = None  # Durum değişikliği için callback
        self.on_ui_update = None      # UI güncellemesi için callback
        self.on_get_coordinate_data = None  # Koordinat verilerini almak için callback
        self.on_coordinate_saved = None  # Koordinat kaydedildiğinde callback
        
        # Durum değişkenleri
        self.is_running = False
        self.is_paused = False
        self.coordinate_mode_active = False
        
        # Klavye dinleyicisi
        self.setup_keyboard_listener()
    
    def setup_keyboard_listener(self):
        """Klavye dinleyicilerini ayarlar"""
        keyboard.on_press_key('p', self.handle_pause_key, suppress=True)
        keyboard.on_press_key('c', self.handle_coordinate_key, suppress=True)
    
    def cleanup(self):
        """Uygulama kapanırken temizlik yapar"""
        keyboard.unhook_all()
    
    def handle_pause_key(self, event):
        """P tuşuna basıldığında çağrılır"""
        try:
            if self.is_running:
                self.toggle_pause()
                return True
        except Exception as e:
            print(f"Duraklama hatası: {e}")
        return False
    
    def handle_coordinate_key(self, event):
        """C tuşuna basıldığında çağrılır"""
        if self.coordinate_mode_active:
            # Aktif koordinat modunda C tuşuna basılırsa koordinatı kaydet
            self.save_current_coordinate()
    
    def save_current_coordinate(self):
        """Mevcut fare pozisyonunu aktif koordinata kaydeder"""
        if not self.coordinate_mode_active:
            return
            
        position = self.model.get_current_mouse_position()
        if position and self.on_coordinate_saved:
            self.on_coordinate_saved(position)
    
    def update_coordinate_position(self, index, position):
        """Koordinat pozisyonunu günceller"""
        self.model.update_coordinate_position(index, position)
    
    def get_current_mouse_position(self):
        """Farenin mevcut pozisyonunu döndürür"""
        return self.model.get_current_mouse_position()
    
    def toggle_coordinate_mode(self):
        """Koordinat kaydetme modunu açıp kapatır"""
        self.coordinate_mode_active = not self.coordinate_mode_active
        return self.coordinate_mode_active
    
    def toggle_click_type(self, index, click_type):
        """Tıklama tipini değiştirir"""
        return self.model.toggle_click_type(index, click_type)
    
    def toggle_automation(self):
        """Otomasyonu başlatır/durdurur"""
        self.is_running = not self.is_running
        self.is_paused = False
        
        if self.is_running:
            print("Otomasyon başlatıldı")
            # Otomasyon başlatıldığında kuyruktaki setleri işle
            self.process_queue()
        else:
            print("Otomasyon durduruldu")
        
        return self.is_running
    
    def toggle_pause(self):
        """Otomasyonu duraklatır/devam ettirir"""
        if self.is_running:
            self.is_paused = not self.is_paused
            if self.on_state_changed:
                self.on_state_changed(self.is_paused)
            print(f"Otomasyon {'duraklatıldı' if self.is_paused else 'devam ediyor'}")
        return self.is_paused
    
    def add_to_queue(self):
        """Aktif seti kuyruğa ekler"""
        active_set = self.model.get_active_set()
        if active_set:
            self.model.add_to_queue(active_set)
            return active_set
        return None
    
    def remove_from_queue(self, index):
        """Seçili seti kuyruktan çıkarır"""
        return self.model.remove_from_queue(index)
    
    def add_new_set(self):
        """Yeni set ekler"""
        return self.model.add_new_set()
    
    def switch_set(self, set_name):
        """Setler arası geçiş yapar"""
        # Mevcut setin verilerini kaydet
        self.save_current_set_data()
        
        # Yeni sete geç
        success = self.model.switch_set(set_name)
        if success and self.on_ui_update:
            self.on_ui_update()
        return success 
    
    def save_current_set_data(self):
        """Mevcut setin verilerini kaydeder"""
        if not self.model.get_active_set() or not self.on_get_coordinate_data:
            return
        
        # UI'dan veri al
        coordinates = self.on_get_coordinate_data()
        if coordinates:
            # Model'e kaydet
            self.model.save_set_data(coordinates)
    
    def save_loop_count(self, count):
        """Döngü sayısını kaydeder"""
        return self.model.save_loop_count(count)
    
    def goto_coordinate(self, index):
        """Seçili koordinata gider"""
        position = self.model.get_coordinate_position(index)
        if position:
            self.model.move_mouse_to(position)
    
    def update_coordinate(self, index):
        """Seçili koordinatı günceller"""
        if self.coordinate_mode_active:
            position = self.model.get_current_mouse_position()
            self.model.update_coordinate_position(index, position)
    
    def update_coordinate_label(self, index, text):
        """Koordinat etiketini günceller"""
        self.model.update_coordinate_label(index, text)
    
    def get_active_set_data(self):
        """Aktif setin verilerini döndürür"""
        return self.model.get_active_set_data()
    
    def get_set_names(self):
        """Tüm set isimlerini döndürür"""
        return self.model.get_set_names()
    
    def get_queue(self):
        """İşlem kuyruğunu döndürür"""
        return self.model.get_queue()
    
    def process_queue(self):
        """Kuyruktaki setleri işler"""
        if not self.is_running:
            return
        
        # Yeni thread oluştur
        self.automation_thread = threading.Thread(target=self._process_queue_worker)
        self.automation_thread.daemon = True
        self.automation_thread.start()
    
    def _process_queue_worker(self):
        """Kuyruk işleme worker'ı"""
        try:
            queue = self.model.get_queue()
            if not queue:
                self.is_running = False
                return
            
            for set_name in queue:
                # Seti yükle
                self.model.load_set(set_name)
                set_data = self.model.get_active_set_data()
                
                # Set verilerini kontrol et
                if not set_data or not set_data['coordinates']:
                    continue
                
                # Döngü sayısı kadar tekrarla
                for _ in range(set_data['loop_count']):
                    # Sıralı koordinatları al
                    coordinates = sorted(
                        set_data['coordinates'], 
                        key=lambda x: x['order']
                    )
                    
                    # Her koordinat için işlem yap
                    for coord in coordinates:
                        # Duraklatma kontrolü
                        while self.is_paused:
                            time.sleep(0.1)
                            if not self.is_running:
                                return
                        
                        # Çalışma kontrolü
                        if not self.is_running:
                            return
                        
                        # Koordinata git ve tıkla
                        if coord['position']:
                            self.model.move_mouse_to(coord['position'])
                            time.sleep(coord['delay'])
                            
                            # Tıklama tipine göre işlem yap
                            if coord['click_type'] == 'left':
                                self.model.left_click()
                            elif coord['click_type'] == 'right':
                                self.model.right_click()
                            elif coord['click_type'] == 'double':
                                self.model.double_click()
                            
                            # Metin girişi varsa yaz
                            if coord['text']:
                                self.model.write_text(coord['text'])
                            
                            time.sleep(coord['delay'])
        
        except Exception as e:
            print(f"Otomasyon hatası: {e}")
        finally:
            # İşlem bittiğinde durumu sıfırla
            self.is_running = False
            self.is_paused = False
            if self.on_state_changed:
                self.on_state_changed(False)
    
    def new_file(self):
        """Yeni dosya oluşturur"""
        # Model'i sıfırla
        self.model.reset()
        
        # İlk seti oluştur
        self.model.add_new_set()
        
        # Durumu sıfırla
        self.is_running = False
        self.is_paused = False
        self.coordinate_mode_active = False
        
        return True
    
    def open_file(self, filename):
        """Dosya açar"""
        try:
            # Mevcut durumu temizle
            self.is_running = False
            self.is_paused = False
            self.coordinate_mode_active = False
            
            # Dosyayı aç
            success = self.model.load_file(filename)
            if success:
                # UI'ı güncelle
                if self.on_ui_update:
                    self.on_ui_update()
                return True
            return False
            
        except Exception as e:
            print(f"Dosya açma hatası: {e}")
            return False
    
    def save_file(self):
        """Dosyayı kaydeder"""
        try:
            # Mevcut setin verilerini kaydet
            self.save_current_set_data()
            
            # Dosyaya kaydet
            return self.model.save_file()
            
        except Exception as e:
            print(f"Dosya kaydetme hatası: {e}")
            return False
    
    def save_file_as(self, filename):
        """Dosyayı farklı kaydeder"""
        try:
            # Mevcut setin verilerini kaydet
            self.save_current_set_data()
            
            # Yeni dosyaya kaydet
            return self.model.save_file_as(filename)
            
        except Exception as e:
            print(f"Dosya kaydetme hatası: {e}")
            return False
    
    def has_current_file(self):
        """Mevcut bir dosya olup olmadığını kontrol eder"""
        return self.model.has_current_file() 
    
    def rename_set(self, old_name, new_name):
        """Set ismini değiştirir"""
        return self.model.rename_set(old_name, new_name)
    
    def add_set_to_queue(self, set_name):
        """Belirli bir seti kuyruğa ekler"""
        return self.model.add_to_queue(set_name) 