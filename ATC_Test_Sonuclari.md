# ATC takım programı test sonuçları

Bu kayıt, kullanıcı tarafından bildirilen fiziksel test sonuçlarını içerir.
Yeni test sonuçları bu dosyaya eklenir.

## T01 — Tek drag punch ve tek die yükleme / boşaltma

- **Tarih:** 2026-11-23
- **Abkant programı:** `ATC_TEST1`.
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
- **Abkant programı:** `ATC_TEST2`.
- **Başlangıç:** Abkantta takım yok; gerekli takımlar warehouse'ta.
- **Program:** BIU-031 punch, boy 40, horn 0; OZU-362 die, boy 200.
- **Yükleme:** Kullanıcı punch ve die yüklemelerinin başarılı olduğunu bildirdi.
  Gerçekleşen slot numaraları bildirilmedi.
- **Punch boşaltma:** Son punch unload edildikten sonra
  `PUNL_U26_Z_DR_DX_TO_PUNCH_PICKPOS_REQ` adımında `tmpInt = 0` iken
  `pDrawerParam6[tmpInt]` erişiminde exception bildirildi.
- **Exception sonrası fiziksel durum:** Kullanıcı punch'ın warehouse'taki
  slotunda, die'ın ise abkantta takılı olduğunu doğruladı.
- **Düzeltme sonrası tekrar test (2026-11-25):** Kullanıcı Test 2'nin load ve
  unload olarak başarıyla tamamlandığını bildirdi. Kullanılan düzeltilmiş
  Punch_Unloading henüz depoya alınmadı; ara değerler bildirilmedi.
- **Sonuç:** Başarılı (exception düzeltmesi sonrası).

## T03 — Aynı programın tekrar yüklenmesi (keep)

- **Tarih:** 2026-11-25
- **Program A:** BIU-031 punch, boy 255, horn 0; OZU-362 die, boy 255.
- **İlk aşama:** Kullanıcı Program A'nın yüklendiğini bildirdi.
- **İkinci aşama:** Kullanıcı güncel changer'larla aynı programı tekrar load
  talep ettiğinde `NO_ACTION` tespit edildiğini ve aşamanın başarılı olduğunu
  bildirdi.
- **Boşaltma / son fiziksel durum:** Henüz bildirilmedi.

## T04 — Aynı punch'ın pozisyonunu değiştirme (planlandı)

- **Tarih:** 2026-11-25
- **Abkant programı:** `ATC-TEST4`.
- **Başlangıç:** Kullanıcı abkantta `ATC_TEST2` programının yüklü olduğunu
  bildirdi. Test 3 planındaki Program A ile bu bilgi arasındaki ilişki henüz
  netleştirilmedi.
- **Plan:** `ATC_TEST2` programındaki punch'ın yalnızca pozisyonu
  değiştirilecek. Program hazırlanacak; test sonucu henüz bildirilmedi.
