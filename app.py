import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
connect = psycopg2.connect("dbname=term user=postgres password=258879")
cur = connect.cursor()  # create cursor


@app.route('/')
def main():
    return render_template("main.html")


@app.route('/return', methods=['post'])
def re_turn():
    return render_template("main.html")


@app.route('/print_my_info', methods=['post'])
def print_my_info():
    send = request.form["send"]
    id = request.form["id"]
    role = request.form["role"]

    if send == 'my wishlist':
        cur.execute("SELECT * FROM wishlist;")  # sql문 쓰기
        wish = cur.fetchall()

        wishlist = []
        for w in wish:
            if w[0] == id:
                wishlist.append(w)
        return render_template("wishlist.html", wishlist=wishlist, id=id)
    elif send == 'my info':
        cur.execute("SELECT * FROM enrollment NATURAL JOIN subject;")  # sql문 쓰기
        enrollment = cur.fetchall()

        my_lecture = []
        for e in enrollment:
            if e[1] == id:
                my_lecture.append([e[5], e[3], e[2], e[4]])

        lectures = []
        if role == 'tutor':
            for e in enrollment:
                if e[2] == id:
                    lectures.append([e[5], e[3], e[1], e[4]])


        return render_template("my_info.html", my_lecture=my_lecture, lectures=lectures, role=role)




@app.route('/admin_function', methods=['post'])
def admin_function():
    send = request.form["send"]

    if send == 'users info':
        cur.execute("SELECT * FROM users;")  # sql문 쓰기
        users = cur.fetchall()
        return render_template("admin_users.html", users=users)
    elif send == 'trades info':
        cur.execute("SELECT * FROM enrollment;")
        trades = cur.fetchall()
        return render_template("admin_trades.html", trades=trades)


@app.route('/admin_pages', methods=['post'])
def admin_pages():
    send = request.form["send"]
    tutee = request.form["tutee"]
    tutor = request.form["tutor"]
    code = request.form["code"]
    name = request.form["name"]
    price = request.form["price"]

    cur.execute("SELECT * FROM account;")  # sql문 쓰기
    account = cur.fetchall()
    for a in account:
        if a[0] == 'admin':
            user_info = a
            break

    if send == 'del':
        cur.execute("DELETE FROM enrollment WHERE tutee='{}' and tutor='{}' and code='{}' and lecture_name='{}' and lecture_price='{}';".format(tutee, tutor, code, name, price))  # sql문 쓰기
        connect.commit()
        cur.execute("SELECT * FROM account;")
        cur.execute("SELECT * FROM lecture;")
        lectures = cur.fetchall()

        cur.execute(
            "SELECT code, lecture_name, tutor, count(tutee) as s_count FROM enrollment GROUP BY code, lecture_name, lecture_price, tutor ORDER BY s_count DESC LIMIT 1;")
        popular_one = cur.fetchall()
        popular = list(popular_one[0])

        cur.execute("SELECT * FROM subject;")
        subjects = cur.fetchall()

        for s in subjects:
            if popular[0] == s[0]:
                popular[0] = s[1]
                break
        return render_template("register_main.html", user_info=user_info, lecture=lectures, popular=popular)


@app.route('/plus_lecture', methods=['post'])
def plus_lecture():
    send = request.form["send"]
    id = request.form["id"]

    cur.execute("SELECT * FROM account;")  # sql문 쓰기
    account = cur.fetchall()
    for a in account:
        if a[0] == id:
            user_info = a
            break
    if send == 'add':
        cur.execute("SELECT * FROM subject;")  # sql문 쓰기
        subject = cur.fetchall()
        return render_template("add_lecture.html", tutor=id, subjects=subject)


@app.route('/each_lecture', methods=['post'])
def each_lecture():
    send = request.form["send"]
    id = request.form["id"]
    code = request.form["code"]
    name = request.form["name"]
    price = request.form["price"]
    tutor = request.form["tutor"]

    cur.execute("SELECT * FROM account;")  # sql문 쓰기
    account = cur.fetchall()
    for a in account:
        if a[0] == id:
            user_info = a
            break

    if send == 'add to wish':
        if tutor == id:
            return render_template("addwish_fail.html")

        cur.execute("INSERT INTO wishlist VALUES('{}', '{}', '{}', '{}', '{}');".format(id, tutor, code, name, price))
        connect.commit()

        cur.execute("select * from wishlist;")
        wish = cur.fetchall()
        wishlist = list()
        for w in wish:
            if w[0] == id:
                wishlist.append(w)
        return render_template("wishlist.html", wishlist=wishlist, id=id)

    elif send == 'register':
        lecture = [code, name, price, tutor]
        price = int(lecture[2])
        cur.execute("SELECT * FROM rating_info;")  # sql문 쓰기
        rating_info = cur.fetchall()
        for r in rating_info:
            if r[0] == user_info[2]:
                discount = float(r[2]) / 100
                discount_price = price * discount
                break
        final = price - discount_price

        return render_template("payment.html", lecture=lecture, user_info=user_info, price=price, discount_price=discount_price,final=final)
    elif send == 'del':
        cur.execute("DELETE FROM wishlist WHERE tutee='{}' and tutor='{}' and code='{}' and lecture_name='{}' and lecture_price='{}';".format(id, tutor, code, name, price))  # sql문 쓰기
        connect.commit()
        cur.execute("SELECT * FROM account;")
        cur.execute("SELECT * FROM lecture;")
        lectures = cur.fetchall()

        cur.execute(
            "SELECT code, lecture_name, tutor, count(tutee) as s_count FROM enrollment GROUP BY code, lecture_name, lecture_price, tutor ORDER BY s_count DESC LIMIT 1;")
        popular_one = cur.fetchall()
        popular = list(popular_one[0])

        cur.execute("SELECT * FROM subject;")
        subjects = cur.fetchall()

        for s in subjects:
            if popular[0] == s[0]:
                popular[0] = s[1]
                break
        return render_template("register_main.html", user_info=user_info, lecture=lectures, popular=popular)


@app.route('/add_lecture', methods=['post'])
def add_lecture():
    send = request.form["send"]
    code = request.form["code"]
    name = request.form["name"]
    price = request.form["price"]
    tutor = request.form["tutor"]

    if send == 'add':

        cur.execute("SELECT * FROM lecture;")
        lecture = cur.fetchall()

        for l in lecture:
            if l[0] == code and l[1] == name and l[2] == price and l[3] == tutor:
                return render_template('add_fail.html')

        cur.execute("INSERT INTO lecture VALUES('{}', '{}', '{}', '{}');".format(code, name, price, tutor))
        connect.commit()

        cur.execute("SELECT * FROM account;")
        users = cur.fetchall()

        for u in users:
            if u[0] == tutor:
                user_info = u
                break
        cur.execute("SELECT * FROM lecture;")
        lectures = cur.fetchall()
        return render_template("register_main.html", user_info=user_info, lecture=lectures)
    else:
        cur.execute("SELECT * FROM account;")
        users = cur.fetchall()

        for u in users:
            if u[0] == tutor:
                user_info = u
                break
        cur.execute("SELECT * FROM lecture;")
        lectures = cur.fetchall()
        return render_template("register_main.html", user_info=user_info, lecture=lectures)


@app.route('/lecture_pay', methods=['post'])
def lecture_pay():
    send = request.form["send"]
    id = request.form["id"]
    role = request.form["role"]
    price = int(float(request.form["price"]))  # 강사
    final = int(float(request.form["final"])) #학생

    code = request.form["code"]
    name = request.form["name"]
    #price 위에 있음
    tutor = request.form["tutor"]

    if send == 'cancel':
        cur.execute("SELECT * FROM account;")
        users = cur.fetchall()

        for u in users:
            if u[0] == id:
                user_info = u
                break
        cur.execute("SELECT * FROM lecture;")
        lectures = cur.fetchall()

        cur.execute(
            "SELECT code, lecture_name, tutor, count(tutee) as s_count FROM enrollment GROUP BY code, lecture_name, lecture_price, tutor ORDER BY s_count DESC LIMIT 1;")
        popular_one = cur.fetchall()
        popular = list(popular_one[0])

        cur.execute("SELECT * FROM subject;")
        subjects = cur.fetchall()

        for s in subjects:
            if popular[0] == s[0]:
                popular[0] = s[1]
                break
        return render_template("register_main.html", user_info=user_info, lecture=lectures, popular=popular)
    elif send == 'confirm':
        #이미 enrollment에 있는지 확인
        cur.execute("SELECT * FROM enrollment;")
        enrollment = cur.fetchall()

        for e in enrollment:
            if e[0] == tutor and e[1] == id and e[2] == name and e[3] == code and e[4] == price:
                return render_template('pay_fail.html')

        if role == 'tutor': #강사 자기강의 결제 제한
            if id == tutor:
                return render_template('pay_fail.html')

        cur.execute("SELECT * FROM account;")  # sql문 쓰기
        account = cur.fetchall()

        for a in account:
            if a[0] == id:
                if a[1] >= final:
                    new_credit_tee = a[1] - final #학생 credit 차감
                    for t in account:
                        if t[0] == tutor: #강사 credit 증가
                            new_credit_tor = t[1] + price
                else:
                    return render_template('pay_fail.html')

        if new_credit_tee < 50000:
            new_rating_tee = 'welcome'
        elif new_credit_tee >= 50000 and new_credit_tee < 100000:
            new_rating_tee = 'bronze'
        elif new_credit_tee >= 100000 and new_credit_tee < 500000:
            new_rating_tee = 'silver'
        else:
            new_rating_tee = 'gold'

        if new_credit_tor < 50000:
            new_rating_tor = 'welcome'
        elif new_credit_tor >= 50000 and new_credit_tor < 100000:
            new_rating_tor = 'bronze'
        elif new_credit_tor >= 100000 and new_credit_tor < 500000:
            new_rating_tor = 'silver'
        else:
            new_rating_tor = 'gold'

        cur.execute("UPDATE account SET credit = '{}', rating = '{}' WHERE id = '{}';".format(new_credit_tee, new_rating_tee, id))
        cur.execute("UPDATE account SET credit = '{}', rating = '{}' WHERE id = '{}';".format(new_credit_tor, new_rating_tor, tutor))

        cur.execute("INSERT INTO enrollment VALUES('{}', '{}', '{}', '{}', '{}');".format(id, tutor, code, name, price))

        connect.commit()

        return render_template('pay_success.html')


@app.route('/register', methods=['post'])
def register():

    id = request.form["id"]
    password = request.form["password"]
    send = request.form["send"]

    cur.execute("SELECT * FROM users;")
    result = cur.fetchall()

    if send == 'login':

        for t in result:
            if t[0] == id and t[1] == password:
                cur.execute("SELECT * FROM account;")
                result2 = cur.fetchall()
                for s in result2:
                    if s[0] == id:
                        user_info = s
                cur.execute("SELECT * FROM lecture;")
                lectures = cur.fetchall()

                cur.execute("SELECT code, lecture_name, tutor, count(tutee) as s_count FROM enrollment GROUP BY code, lecture_name, lecture_price, tutor ORDER BY s_count DESC LIMIT 1;")
                popular_one = cur.fetchall()
                popular = list(popular_one[0])

                cur.execute("SELECT * FROM subject;")
                subjects = cur.fetchall()

                for s in subjects:
                    if popular[0] == s[0]:
                        popular[0] = s[1]
                        break
                return render_template("register_main.html", user_info=user_info, lecture=lectures, popular=popular)

        return render_template("login_fail.html")
    elif send == 'signup':
        return render_template("signup.html")


@app.route('/signup', methods=['post'])
def signup():

    id = request.form["id"]
    password = request.form["password"]
    role = request.form["roles"]
    credit = 10000
    rating = 'welcome'


    cur.execute("SELECT * FROM users;")
    result = cur.fetchall()


    for t in result:
        if t[0] == id:
            return render_template("ID_collision.html")

        cur.execute("INSERT INTO users VALUES('{}', '{}');".format(id, password))
        cur.execute("INSERT INTO account VALUES('{}', '{}', '{}', '{}');".format(id, credit, rating, role))

        connect.commit()
        return render_template("signup_success.html")






if __name__ == '__main__':
    app.run()
