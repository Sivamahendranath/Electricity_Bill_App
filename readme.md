# 💡 Electricity Bill Calculator

This is a simple Python script for calculating the **electricity bill** based on the number of units consumed. It uses a tiered slab rate system, applying different rates for various consumption brackets.

---

## 📂 File

- `electricity bill.txt` — Contains the Python script to compute electricity bills based on units consumed.

---

## 🧮 How It Works

The script calculates the electricity bill using the following rate slabs:

| Slab Range (Units)      | Rate per Unit (₹) |
|-------------------------|-------------------|
| 0 - 50                  | ₹0.50             |
| 51 - 100                | ₹0.75             |
| 101 - 250               | ₹1.20             |
| 251 and above           | ₹1.50             |

The charges are cumulative. For example, if 300 units are consumed:
- First 50 units at ₹0.50
- Next 50 units at ₹0.75
- Next 150 units at ₹1.20
- Remaining 50 units at ₹1.50

---

## How to Run

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

3. Access the app in your browser at `http://localhost:8501`

## Deployment

This app can be deployed to Streamlit Cloud:

1. Push code to GitHub
2. Connect your GitHub repository to Streamlit Cloud
3. Deploy the app with a single click

## Project Structure

```
electricity_bill_app/
├── app.py                # Streamlit entry point
├── bill_calculator.py    # Bill calculation logic
├── requirements.txt      # Dependencies
└── README.md             # Documentation
```

## 🖥️ How to Use

1. Make sure you have Python installed (preferably Python 3.x).
2. Copy the code from `electricity bill.txt` into a Python file, e.g., `bill_calculator.py`.
3. Run the script in your terminal or IDE:
   ```bash
   python bill_calculator.py
   ```
4. Input the number of units consumed when prompted.

---

## 📌 Sample Output

```bash
Enter total units consumed: 300
Electricity Bill: Rs. 365.0
```

---

## ✅ Features

- Supports all unit inputs (positive integers)
- Easy to modify slab rates
- Simple, user-friendly design

---

## 🛠️ Future Improvements

- Add GUI for better user experience
- Include taxes or fixed charges
- Save billing history to file
