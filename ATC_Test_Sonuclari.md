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
- **Abkant programı:** Kullanıcı `ATC-TEST1` ile test edildiğini bildirdi
  (Test 1 için program adı `ATC_TEST1` olarak bildirilmişti).
- **Program A:** BIU-031 punch, boy 255, horn 0; OZU-362 die, boy 255.
- **İlk aşama:** Kullanıcı Program A'nın yüklendiğini bildirdi.
- **İkinci aşama:** Kullanıcı güncel changer'larla aynı programı tekrar load
  talep ettiğinde `NO_ACTION` tespit edildiğini ve aşamanın başarılı olduğunu
  bildirdi.
- **Son fiziksel durum:** Kullanıcı 255 boy BIU-031 punch'ın abkantta takılı
  olduğunu doğruladı. Die'ın son fiziksel durumu henüz bildirilmedi.

## T04 — Aynı punch'ın pozisyonunu değiştirme

- **Tarih:** 2026-11-25
- **Abkant programı:** `ATC_TEST4`.
- **Başlangıç:** Kullanıcı önce `ATC_TEST2` yüklü olduğunu bildirdi, ardından
  bunun yanlış olduğunu ve Test 3'ün `ATC-TEST1` ile yapıldığını düzeltti.
  BIU-031 boy 255 punch abkantta; die durumu henüz bildirilmedi.
- **Plan:** `ATC_TEST1` temel alınarak ayrı bir `ATC_TEST4` programı
  oluşturulacak; yalnızca 255 boy punch'ın pozisyonu değiştirilecek.
- **Changer sonucu (2026-11-26):** Kullanıcı `ATC_TEST4` load talebinde
  PunchChanger'ın `ACTION_REQUIRED`, DieChanger'ın `NO_ACTION` verdiğini
  bildirdi; bu karar beklenen sonuçla uyumlu.
- **İkinci aşama (2026-11-27):** Kullanıcı testin başarılı olduğunu bildirdi.
  Punch_Keeping, BIU-031 boy 255 punch'ı direct slide ile abkant üzerinde
  1400 pozisyonundan 1500 pozisyonuna kaydırdı.
- **Die ve PLC kayıtlarının son durumu:** Henüz ayrıca bildirilmedi.

## T05 — Aynı die'ın pozisyonunu değiştirme

- **Tarih:** 2026-11-27
- **Program:** `ATC_TEST5`, `ATC_TEST4` temel alınarak hazırlanacak.
- **Plan:** Punch, `ATC_TEST4` ile aynı takım ve pozisyonda kalacak;
  die, `ATC_TEST4` pozisyonundan 100 sağa kaydırılacak.
- **Beklenti:** PunchChanger `NO_ACTION`, DieChanger `ACTION_REQUIRED`;
  punch keeping çalıştırılırsa `NO_MOVE`, die keeping uygun koşullarda
  `DIRECT_SLIDE`.
- **Sonuç:** Kullanıcı PunchChanger'ın `NO_ACTION`, DieChanger'ın
  `ACTION_REQUIRED` verdiğini ve Die_Keeping'in `DIRECT_SLIDE` işlemini
  başarıyla yaptığını bildirdi. Gerçek die koordinatları, punch keeping
  davranışı ve PLC kayıtlarının son durumu ayrıca bildirilmedi.

## T06 — ATC_TEST5 programını tekrar yükleme

- **Tarih:** 2026-11-27
- **Program:** `ATC_TEST5` tekrar load ile talep edildi.
- **Sonuç:** Kullanıcı her iki changer'ın `NO_ACTION` verdiğini ve herhangi
  bir hareket oluşmadığını bildirdi. Test başarılı.
