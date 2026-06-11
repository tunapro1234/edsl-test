# CPC — Choice Prediction Competitions (Erev ve ekibi)

İnsan karar davranışını tahmin etme yarışmaları. Format: organizatörler gerçek-paralı lab
deneyleriyle bir **estimation set** yayınlar → takımlar model gönderir → kazanan, sonradan
koşulan **yepyeni problemlerdeki** (competition set) insan davranışını en iyi tahmin eden model.
"Eğri uydurma değil, dokunulmamış veriyi önceden bilme" standardını kurumsallaştıran gelenek.

Organizatörler: Ido Erev (Technion), Eyal Ert (Hebrew U), Ori Plonsky (Duke/Technion),
Reut Apel, Moshe Tennenholtz (Technion), 2010'da Al Roth. Tamamen akademik.

## Deney paradigması (CPC15/18)

- Problem = iki para kumarı arasında seçim; her seçenek 10'a kadar sonuç, ambiguity (olasılığı
  gizli şık) ve payoff korelasyonu mümkün → her problem **12 parametreyle** tanımlı.
- Her problem **25 tur**: ilk 5 tur feedback'siz (tariften karar), 6-25 tam feedback (kazanılan +
  kaçırılan gösterilir) → tek paradigma hem description hem experience ölçer.
- Denekler: Technion + Hebrew U öğrencileri, gerçek ödeme (rastgele bir karar ödenir, ort ~$11).
- Problemler bir **algoritmayla rastgele üretilir** (problem uzayından örnekleme) → cherry-picking
  yok, contamination kontrolü kolay.

## Yıllar

- **2010** (`cpc2010/`): ilk yarışma, 3 pist (description / experience-sampling / repeated
  feedback). Kazananlar ensemble/ACT-R tarzı nicel modeller. Erev, Ert & Roth, JBDM 2010.
- **2015** (`cpc2015/`): 150 problem, 14 klasik anomaliyi tek modelle yakalama hedefi. Kazanan:
  **BEAST** (EV çapası + küçük zihinsel örneklemler; prospect theory DEĞİL). Teori-siz ML
  başvuruları kötü kaldı. Ham veri: 510.750 gözlem, Zenodo record 845873 (kişi ID + demografi +
  12 parametre + tur tur seçim). Erev, Ert, Plonsky et al., Psych Review 2017.
- **2018** (`cpc2018/`): genişletilmiş uzay. İki pist:
  - **Track I** — agrega davranış, 60 YENİ problem, 5 zaman bloğu → ortalama seçim oranı tahmini.
  - **Track II** — BİREYSEL davranış: 30 hedef kişinin 25 problemlik geçmişinden 5 yeni
    problemdeki davranışını tahmin et (digital-twin görevinin 2018 tanımı!).
  - Metrik: MSE → **ENO** (Equivalent Number of Observations: model kaç gerçek deneğin
    ortalamasına bedel). Kazanan: BEAST-GB / Psychological Forest hattı (teori-feature + GBM;
    NHB 2025'te neural netleri de yendiği gösterildi).

## İlgili (`related/choices13k/`)

Peterson, Bourgin et al. Science 2021: aynı paradigmanın MTurk ölçeklisi — 13.006 problem,
~15k kişi, problem başına seçim oranları. github.com/jcpeterson/choices13k. ML ile teori keşfi;
kazanan yorumlanabilir model: bağlama-bağlı parametreli prospect theory.

## B1 ile bağı

1. **Referans dağılımlar**: B1'in risk (Holt-Laury) ve loss-aversion oyunları bu domain —
   ajan popülasyonu seçim oranları problem başına insanla karşılaştırılır.
2. **Hazır ML-tavanı**: BEAST(-GB) tahminleri completeness skoru için bedava tavan.
3. **ENO metriği çalınacak**: "persona popülasyonumuz N gerçek denek değerinde."
4. **Track II şablonu**: bireysel-tahmin görevi, replicant'ın uzun vadeli hedefi.
5. ⚠️ **Contamination**: veriler halka açık → modellerin eğitiminde olabilir; birebir problem
   kullanma, parametreleri perturbe et ya da sadece referans dağılım olarak kullan.

## Klasörler

- `cpc2010/`, `cpc2015/`, `cpc2018/` — yıl başına veri + dökümanlar (indirme logu: SOURCES.md)
- `related/choices13k/` — Peterson seti
- `algorithms/` — açık paylaşılan modeller: BEAST (+ BEAST.sd), Psychological Forest, BEAST-GB
