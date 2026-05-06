"""Basit çeviri compiler - .po dosyalarını .mo'ya çevirir"""
import os
import struct
import array

def generate_mo(po_file, mo_file):
    """PO dosyasını MO formatına çevir (manuel implementation)"""
    translations = {}
    
    with open(po_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    msgid = None
    msgstr = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('msgid "') and not line.startswith('msgid ""'):
            msgid = line[7:-1]  # "msgid \"...\"" → ...
        elif line.startswith('msgstr "') and msgid:
            msgstr = line[8:-1]  # "msgstr \"...\"" → ...
            if msgid and msgstr:
                translations[msgid] = msgstr
            msgid = None
            msgstr = None
    
    # MO dosyası oluştur (basitleştirilmiş)
    keys = sorted(translations.keys())
    offsets = []
    ids = b''
    strs = b''
    
    for k in keys:
        offsets.append((len(ids), len(k), len(strs), len(translations[k].encode('utf-8'))))
        ids += k.encode('utf-8') + b'\x00'
        strs += translations[k].encode('utf-8') + b'\x00'
    
    # MO header (magic number + version)
    output = struct.pack('Iiiiiii', 0x950412de, 0, len(keys), 28, 28 + len(keys) * 8,
                        0, 28 + len(keys) * 16)
    
    # Offsets
    for orig_offset, orig_length, trans_offset, trans_length in offsets:
        output += struct.pack('ii', orig_length, 28 + len(keys) * 16 + orig_offset)
        
    for orig_offset, orig_length, trans_offset, trans_length in offsets:
        output += struct.pack('ii', trans_length, 28 + len(keys) * 16 + len(ids) + trans_offset)
    
    output += ids + strs
    
    with open(mo_file, 'wb') as f:
        f.write(output)

def compile_translations():
    """Tüm çevirileri derle"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    translations_dir = os.path.join(base_dir, 'translations')
    
    print("🔄 Çeviriler derleniyor...\n")
    
    for lang in ['tr', 'en']:
        po_path = os.path.join(translations_dir, lang, 'LC_MESSAGES', 'messages.po')
        mo_path = os.path.join(translations_dir, lang, 'LC_MESSAGES', 'messages.mo')
        
        if os.path.exists(po_path):
            try:
                generate_mo(po_path, mo_path)
                print(f"✅ {lang.upper()} çevirisi derlendi!")
            except Exception as e:
                print(f"❌ {lang.upper()} derlenirken hata: {e}")
        else:
            print(f"⚠️  {po_path} bulunamadı")
    
    print("\n✅ Tamamlandı! Şimdi uygulamayı başlatın: python uygulama.py")

if __name__ == '__main__':
    compile_translations()
