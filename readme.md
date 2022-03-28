# 資料源更新機制
設定排程，定時執行 /house/crawler.py

# 資料庫設計
詳見： /house/model

# API效能保證
未實作，參考方向：
1. 爬蟲抓到資料後，整理資料後再儲存，使API查詢時不再使用like相關語法
2. 針對需要篩選的欄位建立index
3. 查詢時使用redis進行cache

# API規格文件
使用flasgger套件，製作swagger API，運行後於 http://127.0.0.1/apidocs 查看
