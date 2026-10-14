cat > README.md <<'EOF'
# Rubber Farm Management App

แอปพลิเคชันจัดการสวนยางพาราด้วย Python และ PySide6

## ความสามารถ
- คำนวณปริมาณน้ำ
- คำนวณปริมาณปุ๋ย
- วิเคราะห์ต้นทุนและกำไร
- บันทึกข้อมูลสวน
- บันทึกผลผลิตรายเดือน
- คาดการณ์ผลผลิตเบื้องต้น
- แสดงกราฟผลผลิต

## การติดตั้ง

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
