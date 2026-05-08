# Caro 15x15

Du an hien tai la mot game caro 15x15 theo mo hinh:

- Backend: `FastAPI`
- Frontend: `HTML + CSS + JavaScript`
- AI/Bot: cac ham trong `src/caro/ai`

README nay mo ta theo dung cau truc repo hien tai.

## Cau truc hien tai

```text
Caro/
|- main.py
|- requirements.txt
|- README.md
`- src/
   `- caro/
      |- config.py
      |- ai/
      |  |- helper.py
      |  |- min_max.py
      |  `- simple_bot.py
      `- ui/
         |- index.html
         `- scripts.js
```

## Vai tro tung phan

- `main.py`
  - Tao API bang FastAPI.
  - Cung cap endpoint `POST /bot-move` de frontend gui trang thai ban co len va nhan nuoc di cua may.

- `src/caro/config.py`
  - Khai bao cac hang so dung chung nhu kich thuoc ban co, ky hieu quan co.

- `src/caro/ai/helper.py`
  - Cac ham ho tro cho bot:
  - tim nuoc di tiem nang
  - dat / xoa nuoc di
  - kiem tra ket thuc van dau
  - cham diem ban co

- `src/caro/ai/min_max.py`
  - Chua thuat toan `minimax`.

- `src/caro/ai/simple_bot.py`
  - Chua cac cach chon nuoc di cho may.
  - Hien co `choose_move`, `choose_move_random`, `choose_best_move`.
  - `main.py` dang goi `choose_best_move()`.

- `src/caro/ui/index.html`
  - Giao dien trang choi.
  - Ve ban co 15x15 bang HTML/CSS.

- `src/caro/ui/scripts.js`
  - Xu ly tuong tac khi nguoi choi click vao o.
  - Goi API backend de lay nuoc di cua may.

## Luong chay

1. Nguoi choi mo `index.html`.
2. JavaScript khoi tao ban co 15x15.
3. Nguoi choi danh `X`.
4. Frontend gui ma tran ban co hien tai den API `POST /bot-move`.
5. Backend goi `choose_best_move(board)`.
6. API tra ve vi tri `(row, col)` cho may.
7. Frontend cap nhat nuoc di `O` len ban co.

## Cach chay

Hien tai `requirements.txt` moi chi co `streamlit`, trong khi code dang dung `FastAPI`.
Vi vay can cai them cac goi backend can thiet.

### 1. Cai thu vien

```bash
pip install fastapi uvicorn pydantic
```

Neu muon dong bo them theo file hien co:

```bash
pip install -r requirements.txt
```

### 2. Chay backend API

```bash
uvicorn main:app --reload --port 8222
```

Sau khi chay thanh cong, API mac dinh se o:

```text
http://127.0.0.1:8222
```

Thu nhanh:

```text
GET http://127.0.0.1:8222/
```

Se tra ve:

```json
{"message":"Caro AI API is running!"}
```

### 3. Mo frontend

Mo file sau trong trinh duyet:

- [index.html](C:/Users/anhduc/WORKSPACE/CODE/Caro/src/caro/ui/index.html)

Luu y:

- `scripts.js` dang goi API co dia chi co dinh: `http://127.0.0.1:8222/bot-move`
- Backend phai chay truoc thi frontend moi danh duoc voi may.

## Dinh dang du lieu API

### Request

Frontend gui len mot JSON co dang:

```json
{
  "board": [
    [".", ".", ".", "..."],
    [".", "X", ".", "..."]
  ]
}
```

### Response thanh cong

```json
{
  "row": 7,
  "col": 8,
  "status": "success"
}
```

### Response khi khong con nuoc di

```json
{
  "status": "no_moves_available"
}
```

## Ghi chu ky thuat

- Kich thuoc ban co dang dung la `15x15`.
- O trong duoc bieu dien boi `"."` trong Python.
- Nguoi choi dung `X`.
- May dung `O`.
- Backend da mo CORS cho moi origin bang `allow_origins=["*"]`.

## Han che hien tai

- `requirements.txt` chua phan anh dung cac dependency backend dang duoc su dung.
- `scripts.js` hien co dau hieu bi lap ham `updateCell()` va co mot vai doan code cu chua don dep.
- File frontend dang la file tinh, chua co server rieng de phuc vu static files.
- Trong `main.py` dang co mot so comment/literal bi loi ma hoa ky tu.

## Huong phat trien tiep

- Gom frontend vao FastAPI de phuc vu truc tiep thay vi mo file HTML thu cong.
- Don dep `scripts.js`, bo code trung lap.
- Chuan hoa `requirements.txt`.
- Tach ro logic game, API, va AI thanh cac module rieng de de test hon.
