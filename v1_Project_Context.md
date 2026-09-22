# Punch ATC Project Context

## Genel işlem sırası

1. PunchChanger
2. Punch_Unloading
3. Punch_Relocate
4. Punch_DraggUnload
5. Punch_DraggLoad
6. Punch_Keeping
7. Punch_Loading

## FB görevleri

### PunchChanger

Eski ve yeni programı karşılaştırır ve listeleri oluşturur:

- `Retain_UnloadPunchList`
- `Retain_ATCUnloadPunchList`
- `Retain_LoadPunchList`
- `Retain_ATCLoadPunchList`
- `Retain_KeepPunchList`
- `Retain_KeepPunchListNew`
- `Retain_RelocatePunchList`

### Punch_Unloading

Direct unload edilecek punch'ları sök-tak yöntemiyle abkanttan çıkarır.

### Punch_Relocate

Drag yolu üzerinde bulunan keep punch'ları geçici olarak taşır.

Relocate tamamlanınca:

- `PFields_Old` güncellenir.
- `Retain_KeepPunchList` güncellenir.
- `Retain_KeepPunchListNew` değiştirilmez.

Liste anlamları:

- `Retain_KeepPunchList`: mevcut fiziksel punch durumu
- `Retain_KeepPunchListNew`: yeni programdaki hedef durum
- `Retain_RelocatePunchList`: relocate edilecek keep punch alt listesi

### Punch_DraggUnload

Drag unload punch'larını sürükleyerek warehouse'a taşır.

İşlem sonunda `PFields_Old` güncellenir.

### Punch_DraggLoad

Drag load punch'larını warehouse'dan abkant üzerine sürükleyerek yerleştirir.

İşlem sonunda `PFields_Old` güncellenir.

### Punch_Keeping

Relocate edilmiş veya edilmemiş keep punch'ları yeni programdaki final pozisyonlarına taşır.

Hedef veriler:

```text
Retain_KeepPunchList[i,*]    mevcut fiziksel durum
Retain_KeepPunchListNew[i,*] yeni program hedef durumu
```

## Punch_Keeping için önemli kural

Punch_Keeping yalnızca keep listelerini değil, `PFields_Old` içindeki diğer dolu punch'ları da engel olarak dikkate almalıdır.

Bunun nedeni:

- `Punch_DraggLoad` ile yüklenen punch'lar artık `PFields_Old` içinde bulunur.
- Bu punch'lar `Retain_KeepPunchList` içinde olmayabilir.
- Bu nedenle Punch_Keeping çakışma analizinde bunlar sabit obstacle olarak değerlendirilmelidir.

## Punch_Keeping analiz mantığı

### Keep punch'lar

Aktif keep punch'lar:

```text
Retain_KeepPunchList
Retain_KeepPunchListNew
```

üzerinden alınır.

### Sabit obstacle punch'lar

`PFields_Old[i,3] <> ''` olan ve aktif keep punch'a ait olmayan satırlar obstacle olarak değerlendirilir.

Obstacle range:

```text
ObstacleStart := CurrentZ - Width / 2
ObstacleEnd   := CurrentZ + Width / 2
```

### Çakışma kontrolü

Hem hedef pozisyon kontrolünde hem de sweep kontrolünde aşağıdakiler dikkate alınır:

1. Diğer aktif keep punch'lar
2. Daha önce final pozisyonuna yerleşmiş keep punch'lar
3. `PFields_Old` içinde bulunan drag-load punch'lar
4. Diğer sabit dolu punch satırları

## RelocateThreshold

`PunchChanger` içinde hesaplanır:

```text
RelocateThreshold :=
  MAX(
    RightmostDragUnloadPos,
    RightmostDragLoadPos
  );
```

Relocate listesi:

```text
IF CurrentPosition < RelocateThreshold THEN
  relocate edilir
END_IF;
```

Ayrıca `Retain_KeepPunchList` içindeki `RelocateThreshold` değerinden büyük pozisyonlar taranır.

Bunlar arasındaki en büyük pozisyon:

```text
MaxKeepAboveThreshold
```

olarak seçilir.

Sonuç:

```text
IF FoundKeepAboveThreshold THEN
  RelocateTrashold_Value := MaxKeepAboveThreshold;
ELSE
  RelocateTrashold_Value := RelocateThreshold;
END_IF;
```

## Önemli veri alanları

- Sütun `3`: punch/tool adı
- Sütun `6`: Z pozisyonu
- Sütun `7`: punch genişliği
- Sütun `8`: rotation bilgisi
- Sütun `9`: horn bilgisi
- Sütun `10`: drawer numarası
- Sütun `11`: slot numarası
- Sütun `12`: kaynak/orijinal index

## Mevcut kararlar

- `Retain_KeepPunchList` relocate sonrasında senkronize edilecek.
- `Retain_KeepPunchListNew` yeni program hedefi olduğu için değiştirilmemeli.
- `PFields_Old` işlem sırasındaki güncel fiziksel durum olarak kullanılmalı.
- Punch_Keeping çakışma analizi `PFields_Old` obstacle'larını da görmeli.
- Drag-load ile gelen punch'lar Punch_Keeping sırasında sabit engel kabul edilmeli.