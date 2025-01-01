import json
import pyautogui
import keyboard
from utils.constants import Constants

class AutomationModel:
    def __init__(self):
        self.constants = Constants()
        
        # Veri yapısı
        self.sets = {}  # Tüm setler
        self.active_set = None  # Aktif set
        self.queue = []  # İşlem kuyruğu
        self.current_file = None  # Açık dosya
        
        # İlk seti oluştur
        self.add_new_set()
    
    def reset(self):
        """Tüm verileri sıfırlar"""
        self.sets.clear()
        self.queue.clear()
        self.current_file = None
        self.active_set = None
    
    def add_new_set(self):
        """Yeni set ekler"""
        # Yeni set adını belirle
        set_count = len(self.sets) + 1
        set_name = f"Set {set_count}"
        
        # Set verisi oluştur
        self.sets[set_name] = {
            'loop_count': 1,
            'coordinates': []
        }
        
        # İlk set ise aktif set yap
        if not self.active_set:
            self.active_set = set_name
        
        return set_name
    
    def get_active_set(self):
        """Aktif seti döndürür"""
        return self.active_set
    
    def get_active_set_data(self):
        """Aktif setin verilerini döndürür"""
        if self.active_set and self.active_set in self.sets:
            return self.sets[self.active_set]
        return None
    
    def get_set_names(self):
        """Tüm set isimlerini döndürür"""
        return list(self.sets.keys())
    
    def rename_set(self, old_name, new_name):
        """Set ismini değiştirir"""
        if old_name in self.sets and new_name not in self.sets:
            # Set verilerini yeni isimle kaydet
            self.sets[new_name] = self.sets.pop(old_name)
            
            # Aktif seti güncelle
            if self.active_set == old_name:
                self.active_set = new_name
            
            # Kuyruğu güncelle
            self.queue = [new_name if name == old_name else name for name in self.queue]
            
            return True
        return False
    
    def switch_set(self, set_name):
        """Setler arası geçiş yapar"""
        if set_name in self.sets:
            self.active_set = set_name
            return True
        return False
    
    def save_set_data(self, coordinates):
        """Set verilerini kaydeder"""
        if self.active_set:
            # Mevcut koordinatları koru
            current_coordinates = self.sets[self.active_set]['coordinates']
            
            # Yeni koordinatları güncelle
            for i, coord in enumerate(coordinates):
                if i < len(current_coordinates):
                    # Mevcut koordinatı güncelle
                    current = current_coordinates[i]
                    current.update({
                        'label': coord['label'],
                        'click_type': coord['click_type'],
                        'text': coord['text'],
                        'delay': coord['delay'],
                        'order': coord['order']
                    })
                    # Pozisyonu sadece varsa güncelle
                    if coord['position']:
                        current['position'] = coord['position']
                else:
                    # Yeni koordinat ekle
                    current_coordinates.append(coord)
    
    def save_loop_count(self, count):
        """Döngü sayısını kaydeder"""
        if self.active_set:
            self.sets[self.active_set]['loop_count'] = count
    
    def get_coordinate_position(self, index):
        """Koordinat pozisyonunu döndürür"""
        if self.active_set:
            coordinates = self.sets[self.active_set]['coordinates']
            if 0 <= index < len(coordinates):
                return coordinates[index].get('position')
        return None 
    
    def get_current_mouse_position(self):
        """Farenin mevcut pozisyonunu döndürür"""
        x, y = pyautogui.position()
        return {'x': x, 'y': y}
    
    def move_mouse_to(self, position):
        """Fareyi belirtilen pozisyona taşır"""
        if position and 'x' in position and 'y' in position:
            pyautogui.moveTo(position['x'], position['y'])
    
    def left_click(self):
        """Sol tıklama yapar"""
        pyautogui.click(button='left')
    
    def right_click(self):
        """Sağ tıklama yapar"""
        pyautogui.click(button='right')
    
    def double_click(self):
        """Çift tıklama yapar"""
        pyautogui.doubleClick()
    
    def write_text(self, text):
        """Metin yazar"""
        if text:
            pyautogui.write(text)
    
    def _create_default_coordinate(self, index):
        """Varsayılan koordinat verisi oluşturur"""
        return {
            'label': f"K {index+1}: ",
            'click_type': 'left',
            'text': '',
            'delay': self.constants.COORDINATES['default_delay'],
            'order': index,
            'position': None
        }
    
    def update_coordinate_position(self, index, position):
        """Koordinat pozisyonunu günceller"""
        if self.active_set:
            coordinates = self.sets[self.active_set]['coordinates']
            while len(coordinates) <= index:
                coordinates.append(self._create_default_coordinate(len(coordinates)))
            
            # Pozisyonu güncelle
            coordinates[index]['position'] = position
            
            # Eğer etiket varsayılan ise, pozisyon bilgisini ekle
            if coordinates[index]['label'] == f"K {index+1}: ":
                coordinates[index]['label'] = f"K {index+1}: ({position['x']}, {position['y']})"
    
    def update_coordinate_label(self, index, text):
        """Koordinat etiketini günceller"""
        if self.active_set:
            coordinates = self.sets[self.active_set]['coordinates']
            while len(coordinates) <= index:
                coordinates.append(self._create_default_coordinate(len(coordinates)))
            coordinates[index]['label'] = text
    
    def toggle_click_type(self, index, click_type):
        """Tıklama tipini değiştirir"""
        if self.active_set:
            coordinates = self.sets[self.active_set]['coordinates']
            while len(coordinates) <= index:
                coordinates.append(self._create_default_coordinate(len(coordinates)))
            coordinates[index]['click_type'] = click_type
            return click_type
        return None
    
    def add_to_queue(self, set_name):
        """Seti kuyruğa ekler"""
        if set_name in self.sets and set_name not in self.queue:
            self.queue.append(set_name)
            return True
        return False
    
    def remove_from_queue(self, index):
        """Seti kuyruktan çıkarır"""
        if 0 <= index < len(self.queue):
            self.queue.pop(index)
            return True
        return False
    
    def get_queue(self):
        """İşlem kuyruğunu döndürür"""
        return self.queue.copy() 
    
    def load_file(self, filename):
        """Dosyadan veri yükler"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # Veri formatını kontrol et
                if not isinstance(data, dict) or 'sets' not in data or 'queue' not in data:
                    return False
                
                # Her setin veri yapısını kontrol et ve düzelt
                for set_name, set_data in data['sets'].items():
                    if 'loop_count' not in set_data:
                        set_data['loop_count'] = 1
                    if 'coordinates' not in set_data:
                        set_data['coordinates'] = []
                    
                    # Her koordinatın veri yapısını kontrol et
                    for i, coord in enumerate(set_data['coordinates']):
                        default = self._create_default_coordinate(i)
                        for key in default:
                            if key not in coord:
                                coord[key] = default[key]
                
                # Verileri yükle
                self.sets = data['sets']
                self.queue = data['queue']
                self.current_file = filename
                
                # Aktif seti ayarla
                if self.sets:
                    self.active_set = next(iter(self.sets))
                else:
                    self.active_set = None
                
                return True
                
        except Exception as e:
            print(f"Dosya yükleme hatası: {e}")
            return False
    
    def save_file(self):
        """Mevcut dosyaya kaydeder"""
        if not self.current_file:
            return False
        
        return self.save_file_as(self.current_file)
    
    def save_file_as(self, filename):
        """Yeni dosyaya kaydeder"""
        try:
            # Kaydedilecek veriyi hazırla
            data = {
                'sets': self.sets,
                'queue': self.queue
            }
            
            # Dosyaya kaydet
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            
            self.current_file = filename
            return True
            
        except Exception as e:
            print(f"Dosya kaydetme hatası: {e}")
            return False
    
    def has_current_file(self):
        """Mevcut bir dosya olup olmadığını kontrol eder"""
        return bool(self.current_file)
    
    def load_set(self, set_name):
        """Belirtilen seti yükler"""
        if set_name in self.sets:
            self.active_set = set_name
            return True
        return False 