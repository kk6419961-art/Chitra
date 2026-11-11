# Chitra APK मोबाइल से बनाना

यह प्रोजेक्ट अभी शुरुआती डेवलपमेंट स्कैफोल्ड है। APK GitHub Actions के क्लाउड बिल्ड से बनाया जा सकता है; इसके लिए फोन में Android Studio इंस्टॉल करने की जरूरत नहीं है।

1. ZIP को फोन में डाउनलोड करके ZArchiver जैसे archive ऐप से Extract करें।
2. GitHub पर साइन इन करें और नया **Public** या **Private** repository बनाएं, नाम `chitra-platform` रख सकते हैं।
3. Extract किए गए प्रोजेक्ट के अंदर की सभी फाइलें और `.github` फ़ोल्डर repository के root में अपलोड करें। ZIP फाइल को अकेले अपलोड न करें। Hidden `.github` फ़ोल्डर भी शामिल होना चाहिए।
4. GitHub repository में **Actions** खोलें। `Build Chitra Android APK` workflow चुनें और **Run workflow** दबाएं।
5. Build सफल होने पर workflow run के नीचे **Artifacts** में `chitra-debug-apk` मिलेगा। उसे डाउनलोड करके ZIP extract करें; अंदर `app-debug.apk` होगा।
6. APK खोलकर Android के prompt पर इस स्रोत से install की अनुमति दें, फिर Install करें।

अगर build लाल/failed दिखे, तो Actions की error का screenshot भेजें।

## जरूरी सीमा
- यह केवल debug/test APK बनाता है, Play Store release नहीं।
- Backend अभी अपने-आप online नहीं होगा; login/video upload जैसी server सुविधाओं के लिए backend deploy और app में API URL configure करना बाकी है।
- अभी यह production-ready या पूर्ण YouTube-जैसा ऐप नहीं है।
