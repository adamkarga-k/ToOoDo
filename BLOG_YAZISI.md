# Ekranımın Tepesinde Bir Kedi Uyuyor: Minimalist Masaüstü Şeridim "ToOoDo" Nasıl Doğdu?

Hepimizin masasında ya da aklının bir köşesinde uçuşan onlarca küçük görev var. *"Şu kitabı sisteme yükle"*, *"mizanpajı tamamla"*, *"akşama ekmek al"*, *"Sezer Abi'ye fikir sor"...*

Peki biz bu görevleri nerede tutuyoruz? 

Muhtemelen çoğumuz gibi siz de Notion, Todoist, Trello veya TickTick gibi onlarca farklı araç denediniz. Hepsi harika, hepsi özellik dolu. Ama dürüst olalım: Günün ortasında aklıma iki kelimelik bir not geldiğinde; açılması 5 saniye süren, arkada 500 MB RAM tüketen, onlarca sekmesi, etiketi ve alt menüsü olan bir "proje yönetim devini" açmak bazen yapılacak işin kendisinden daha yorucu oluyor. Ya da masaüstüne rastgele saçılan yapışkan notlar (Sticky Notes) bir süre sonra ekranı çöplüğe çeviriyor; pencerelerin arkasında kaybolup gidiyor.

Ben sadece **gözümün önünde duran**, **bilgisayarımı hiç yormayan** ve bana telaş değil **huzur veren** bir şey istiyordum. Bir masanın üzerine iliştirilmiş incecik bir kağıt şerit gibi...

Ve böylece **ToOoDo** doğdu.

---

## 🌿 Ekranın Üstünde İncecik Bir Parşömen

ToOoDo, ekranın en üstünde sadece 28 piksellik yer kaplayan yatay bir şerit. 

Onu tasarlarken en çok önemsediğim şeylerden biri **ekranla tam bütünleşmesiydi**. Windows'un AppBar altyapısını kullanarak sistemi öyle bir ayarladım ki; Chrome’u, tarayıcınızı veya Word’ü tam ekran yapsanız bile pencereler ToOoDo’nun hemen alt sınırına kenetleniyor. Yani hiçbir pencere onun üstünü kapatmıyor, o da hiçbir açık pencerenizin düğmelerini örtmüyor. Sürekli orada, tam karşınızda ama asla bağırmayan bir sessizlikte.

Renk paletini seçerken de yapay, parlak neon arayüzlerden kaçındım:
- **Açık Parşömen Modu:** Fildişi ve krem tonlarında, üzerine kurşun kalemle not alınmış gerçek bir defter sayfası hissi.
- **Koyu Kraft (Gece Modu):** Gece çalışırken gözü dinlendiren sıcak kömür ve mat bej tonları.

Bir işi tamamladığınızda onay kutusuna dokunuyorsunuz; yeşil zarif bir tik beliriyor, kelimenin üstü hafif bir kurşun kalem çizgisiyle çiziliyor ve görev şeridin sonuna doğru usulca kayıyor. Hemen yok olmuyor; gün boyu başardığınız işleri görüp o tatlı tatmin duygusunu yaşayabiliyorsunuz.

---

## 🐱 Ve Sonra Masaüstüme Bir Kedi Geldi

ToOoDo tek başına da çok sade ve işlevseldi ama çalışırken eksik olan bir şey vardı: **Ruh.**

Ekran başında saatlerce tasarım yaparken, kod yazarken veya yazı yazarken insan yanında küçük bir yaşam belirtisi arıyor. Ben de şeridin sol köşesine pixel art animasyonlu minik bir kedi arkadaşı eklemeye karar verdim.

Ama öyle süs niyetine duran bir kedi değil; sizinle beraber yaşayan bir can:

- **Sol Köşede Uyuklama:** Gün boyu köşesinde kıvrılıp mışıl mışıl uyuyor, nefes alıp veriyor, ara sıra tatlı tatlı esniyor.
- **Meraklı Fare Takibi:** Fare imlecini ToOoDo şeridinin üzerine getirdiğiniz anda kulaklarını dikip hemen uyanıyor. İmlecinizin olduğu yere doğru pıtır pıtır koşuyor, farenin yanında durup arka ayakları üstüne dikilerek patisini fareye doğru uzatıyor.
- **Geciken İşlere Küçük Bir Uyarı:** Eğer vadesi yaklaşan veya geciken acil bir göreviniz varsa, kedi köşesinden kalkıp o görevin yanına kadar yürüyor ve patisiyle karta dokunarak *"Hey, buna bir baksan iyi olur"* dercesine sizi uyarıyor.
- **Günün En Güzel Anı (Huzurlu Ekmek Somunu):** Listedeki tüm aktif işleri bitirdiğinizde... İşte o an kedi keyifle geriniyor, meşhur "ekmek somunu" (loaf) pozisyonunu alıyor ve derin bir uykuya dalıyor. Sırf kediyi o huzurlu uykusuna kavuşturmak için bile insan kalan son 2 işi bitirmek istiyor!

İsterseniz sağdaki menüden kürkünün rengini de değiştirebiliyorsunuz: Kül Grisi (benim favorim), Sarman Tekir veya Pamuk Beyazı.

---

## ⚡ 18 MB RAM ve %0 CPU: Hafiflik Bir Tercihtir

Bugün basit bir metin düzenleyicinin bile arkada bir Chrome tarayıcı motoru (Electron) çalıştırdığı ve bilgisayarın kaynaklarını sömürdüğü bir çağdayız. 

ToOoDo’yu geliştirirken taviz vermediğim en büyük ilke **hafiflik** oldu. Saf Python ve doğrudan Windows Win32 API'leri üzerine inşa edildi:
- Çalışırken sadece **~18 MB RAM** harcıyor (neredeyse sıfır!).
- İşlemci (CPU) kullanımı tam olarak **%0.0**.
- Klavyeden `Alt + Shift + T` tuşlarına bastığınız anda, hangi oyunda veya programda olursanız olun şerit hemen odaklanıyor ve tek satırda yeni notunuzu ekleyebiliyorsunuz.
- Üstelik hiçbir veriniz internete, yabancı sunuculara veya buluta gitmiyor. Her şey kendi bilgisayarınızda, güvenle saklanıyor.

---

## 🚀 Siz de Denemek İster misiniz?

ToOoDo'yu sadece kendim için değil, gün boyu bilgisayar başında çalışan, basitlik arayan herkes için açık kaynak olarak paylaştım.

Kullanmak için bilgisayarınızda Python veya kodlama ortamı olmasına **kesinlikle gerek yok**. Hazırladığım tek bir `.exe` dosyasını indirip çift tıklamanız yeterli:

- 🔗 **GitHub Proje Sayfası:** [github.com/adamkarga/ToOoDo](https://github.com/adamkarga/ToOoDo)
- 📥 **Doğrudan İndirme:** [ToOoDo.exe İndir](https://github.com/adamkarga/ToOoDo/releases/latest/download/ToOoDo.exe)
- 🐦 **Görüşlerinizi Paylaşın:** [@adamkarga_](https://x.com/adamkarga_)

Eğer siz de masaüstünüzün bir köşesinde hem işlerinizi toparlayacak hem de ara sıra esneyip size eşlik edecek minik bir dost isterseniz, ToOoDo'ya mutlaka bir şans verin. 

Masanız sade, kediniz uykulu, zihniniz ferah olsun! 🌿🐾
