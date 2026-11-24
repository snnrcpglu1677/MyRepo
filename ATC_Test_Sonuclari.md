# ATC takım programı test sonuçları

Bu kayıt, kullanıcı tarafından bildirilen fiziksel test sonuçlarını içerir.
Yeni test sonuçları bu dosyaya eklenir.

## T01 — Tek drag punch ve tek die yükleme / boşaltma

- **Tarih:** 2026-11-23
- **Başlangıç:** Abkantta takım yok; gerekli takımlar warehouse'ta.
- **Program:** BIU-031 punch, boy 255, horn 0; OZU-362 die, boy 255.
- **Yükleme:** Punch drawer 1, slot 4'ten seçilerek drag load ile;
  die drawer 1, slot 1'den seçilerek die load ile yüklendi.
- **Boşaltma:** Unload talebiyle punch drag unload, die ise die unload
  ile warehouse'taki yerlerine geri konuldu.
- **Sonuç:** Başarılı; kullanıcı yükleme ve boşaltmada sorun bildirmedi.
- **Son durum:** Abkantta takım yok; kullanıcı warehouse'un tam kapasitede
  olduğunu bildirdi.

Pozisyonlar ve ara liste içerikleri bu test için bildirilmedi.

## T02 — Tek direct punch ve 200 boy die yükleme / boşaltma

- **Tarih:** 2026-11-24
- **Başlangıç:** Abkantta takım yok; gerekli takımlar warehouse'ta.
- **Program:** BIU-031 punch, boy 40, horn 0; OZU-362 die, boy 200.
- **Yükleme:** Kullanıcı punch ve die yüklemelerinin başarılı olduğunu bildirdi.
  Gerçekleşen slot numaraları bildirilmedi.
- **Punch boşaltma:** Son punch unload edildikten sonra
  `PUNL_U26_Z_DR_DX_TO_PUNCH_PICKPOS_REQ` adımında `tmpInt = 0` iken
  `pDrawerParam6[tmpInt]` erişiminde exception bildirildi.
- **Die boşaltma ve son fiziksel durum:** Bildirilmedi.
- **Sonuç:** Tamamlanmadı; punch unload sonrası exception araştırılıyor.
