from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Khởi tạo Flask app
app = Flask(__name__)
app.secret_key = "khoacuoi_ky"

# Cấu hình SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0934136619Tai@localhost/qlsv'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Định nghĩa model cho database
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    gender = db.Column(db.String(10), nullable=False)
    dob = db.Column(db.String(10), nullable=False)
    major = db.Column(db.String(100), nullable=True)
    mssv = db.Column(db.String(20), nullable=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):  # Kế thừa từ UserMixin
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Các thuộc tính cần thiết cho Flask-Login
    @property
    def is_active(self):
        return True  # Hoặc có thể kiểm tra điều kiện nào đó

    @property
    def is_authenticated(self):
        return True  # Người dùng đã xác thực

    @property
    def is_anonymous(self):
        return False  # Người dùng không phải là anonymous

# Tạo database và bảng
with app.app_context():
    db.create_all()

# Routes
@app.route("/")
def index():
    people = Person.query.all()
    return render_template("index.html", people=people)

# Route đăng ký
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Kiểm tra xem tên người dùng và email đã tồn tại chưa
        existing_user = User.query.filter((User .username == username) | (User .email == email)).first()
        if existing_user:
            flash("Tên đăng nhập hoặc email đã tồn tại!", "error")
            return redirect(url_for("register"))

        # Mã hóa mật khẩu với phương thức mặc định
        hashed_password = generate_password_hash(password)

        if username and email and password:
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Đăng ký thành công, bạn có thể đăng nhập ngay!", "success")
            return redirect(url_for("login"))
        else:
            flash("Vui lòng điền đầy đủ thông tin!", "error")
    return render_template("register.html")

# Route đăng nhập
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for("index"))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng!", "error")
    return render_template("login.html")

# Route đăng xuất
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Đăng xuất thành công!", "success")
    return redirect(url_for("login"))

# Cấu hình user_loader để Flask-Login có thể lấy thông tin user từ database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/add", methods=["GET", "POST"])
def add_person():
    if request.method == "POST":
        name = request.form.get("name")
        address = request.form.get("address")
        gender = request.form.get("gender")
        dob = request.form.get("dob")
        major = request.form.get("major")  # Lấy ngành học từ form
        mssv = request.form.get("mssv") # Lấy MSSV từ form

        if name and gender and dob:
            new_person = Person(name=name, address=address, gender=gender, dob=dob, major=major, mssv=mssv)
            db.session.add(new_person)
            db.session.commit()
            flash("Đã thêm thông tin thành công!", "success")
            return redirect(url_for("index"))
        else:
            flash("Vui lòng điền đầy đủ các thông tin bắt buộc!", "error")
    
    return render_template("add_person.html")  # Hiển thị form thêm người

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_person(id):
    person = Person.query.get_or_404(id)
    if request.method == "POST":
        person.name = request.form.get("name")
        person.address = request.form.get("address")
        person.gender = request.form.get("gender")
        person.dob = request.form.get("dob")
        person.major = request.form.get("major")  # Lấy ngành học từ form
        person.mssv = request.form.get("mssv")
        db.session.commit()
        flash("Đã cập nhật thông tin thành công!", "success")
        return redirect(url_for("index"))
    return render_template("manage.html", person=person)

@app.route("/delete/<int:id>")
@login_required
def delete_person(id):
    person = Person.query.get_or_404(id)

    # Kiểm tra quyền xóa
    if current_user.is_admin:  # Kiểm tra nếu người dùng là admin
        db.session.delete(person)
        db.session.commit()
        flash("Đã xóa thông tin thành công!", "success")
    elif current_user.id == person.id:  # Người dùng chỉ có thể xóa thông tin của chính mình
        db.session.delete(person)
        db.session.commit()
        flash("Đã xóa thông tin thành công!", "success")
    else:
        flash("Bạn không có quyền xóa thông tin này!", "error")

    return redirect(url_for("index"))

@app.route("/export/excel")
def export_excel():
    people = Person.query.all()
    data = [{"ID": p.id, "Họ tên": p.name, "Địa chỉ": p.address, "Giới tính": p.gender, "Ngày sinh": p.major, "Ngành Học": p.mssv, "Mã số sinh viên": p.dob} for p in people]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Danh sách')
    output.seek(0)
    return send_file(output, download_name="danh_sach.xlsx", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5050)
