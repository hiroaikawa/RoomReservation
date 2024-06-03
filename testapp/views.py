from flask import render_template, request, redirect, url_for, jsonify, flash, session
from werkzeug.exceptions import HTTPException
import pymysql
import traceback
from testapp import app, login_manager
import json
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from wtforms import (StringField, PasswordField, BooleanField,
                     RadioField, SelectField,SubmitField, ValidationError)
from testapp import user

def getConnection():
  return pymysql.connect(
    host=app.config['DB_HOST'],
    port=app.config['DB_PORT'],
    db=app.config['DB_NAME'],
    user=app.config['DB_USER'],
    passwd=app.config['DB_PASS'],
    charset='utf8',
  )

def getInitialResponse():
    return {}, 200

@app.errorhandler(Exception)
def handle_exception(e):
    traceback.print_exc()
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return render_template("testapp/500_generic.html", message=str(e)), 500

@login_manager.user_loader
def load_user(user_id):
    return user.User.query.get(int(user_id))
    #return user.User.objects(pk=int(user_id)).first()

login_manager.login_view = 'login'

def localize_callback(*args, **kwarg):
    return 'You need to sign in to access this page.'
login_manager.localize_callback = localize_callback

class LoginForm(FlaskForm):
    public_id = StringField('ID')
    password = PasswordField('Password')
    submit = SubmitField('Sign in')
    def validate_on_submit(self):
        return True

@app.route('/')
@login_required
def index():
    return render_template('testapp/index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        userElem = user.User.query.filter_by(public_id=form.public_id.data).first()
        if userElem is not None:
            if userElem.check_password(form.password.data):
                login_user(userElem)
                # session['user_id'] = userElem.id
                next = request.args.get('next')
                if next == None or not next[0] == '/':
                    next = url_for('index')
                return redirect(next)
                
            else:
                flash('Specified password is incorrect.')
        else:
            flash('Specified ID does not exist.')

    return render_template('testapp/login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/room_groups')
@login_required
def room_group_list():
    conn = getConnection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        sql = """
            select mas_room_group.id as id, mas_room_group.name as name, count(mas_room.id) as room_count from mas_room_group
            left outer join mas_room on mas_room_group.id = mas_room.room_group_id 
            group by mas_room_group.id
            order by mas_room_group.name;
            ;
        """
        cur.execute(sql)
        room_group_list = cur.fetchall()
    conn.close()
    return render_template('testapp/room_group_list.html', room_group_list=room_group_list)

@app.route('/room_groups/<int:id>/delete', methods=['POST'])
@login_required
def room_group_delete(id):  
    conn = getConnection()
    res, status_code = getInitialResponse()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            sql = """
                delete from mas_room_group where id = %s;
                ;
            """
            cur.execute(sql, (int(id),))
        conn.commit()
    except Exception as e:
        traceback.print_exc()
        conn.rollback()
        status_code = 500
        res["message"] = str(e)
    finally:
        conn.close()
    return jsonify(res), status_code

@app.route('/add_room_group', methods=['GET', 'POST'])
@login_required
def add_room_group():
    if request.method == 'GET':
        return render_template('testapp/add_room_group.html')
    if request.method == 'POST':
        res, status_code = getInitialResponse()
        conn = getConnection()
        try:
            form_name = request.form.get('name')
            if form_name is None:
                raise ValueError("name should not be null.")
            form_name = str.strip(form_name)
            if not form_name:
                raise ValueError("Name should not be empty or only spaces.")

            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                sql = """
                    insert into mas_room_group (name) values(%s);
                    ;
                """
                cur.execute(sql, (form_name),)
            conn.commit()
        except Exception as e:
            traceback.print_exc()
            conn.rollback()
            status_code = 500
            res["message"] = str(e)
        finally:
            conn.close()
        return jsonify(res), status_code
    
@app.route('/room_groups/<int:id>/update', methods=['POST'])
@login_required
def room_group_update(id):
    res, status_code = getInitialResponse()
    conn = getConnection()
    try:
        form_name = request.form.get('name')
        if form_name is None:
            raise ValueError("name is null!")
        form_name = str.strip(form_name)
        if not form_name:
            raise ValueError("Name should not be empty or only spaces.")
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            sql = """
                update mas_room_group
                SET name = %s
                where id = %s;
                ;
            """
            cur.execute(sql, (form_name, int(id)),)
        conn.commit()
    except Exception as e:
        traceback.print_exc()
        conn.rollback()
        status_code = 500
        res["message"] = str(e)
    finally:
        conn.close()
    return jsonify(res), status_code
    
@app.route('/room_groups/<int:id>')
@login_required
def room_group_detail(id):
    room_group = {}
    conn = getConnection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        sql = """
            select name from mas_room_group
            where id = %s;
            ;
        """
        cur.execute(sql, (int(id),))
        room_group_list = cur.fetchall()
        if len(room_group_list) != 1:
            raise ValueError("group name count is not one. id={0}".format(id))
        print(room_group_list)
        room_group['name'] = room_group_list[0]['name'];
        room_group['id'] = id
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        sql = """
            select id, name from mas_room
            where room_group_id = %s
            order by mas_room.name
            ;
        """
        cur.execute(sql, (int(id),))
        room_list = cur.fetchall()
    conn.close()
    return render_template('testapp/room_group_detail.html', room_list=room_list, room_group=room_group)

@app.route('/room_groups/<int:id>/add_room', methods=['GET', 'POST'])
@login_required
def add_room(id):
    if request.method == 'GET':
        room_group = {}
        conn = getConnection()
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            sql = """
                select name from mas_room_group
                where id = %s;
                ;
            """
            cur.execute(sql, (int(id),))
            room_group_list = cur.fetchall()
            if len(room_group_list) != 1:
                raise ValueError("group name count is not one. id={0}".format(id))
            print(room_group_list)
            room_group['name'] = room_group_list[0]['name'];
            room_group['id'] = id
        conn.close()
        return render_template('testapp/add_room.html', room_group=room_group)
    if request.method == 'POST':
        res, status_code = getInitialResponse()
        conn = getConnection()
        try:
            form_name = request.form.get('name')
            if form_name is None:
                raise ValueError("name is null!")
            form_name = str.strip(form_name)
            if not form_name:
                raise ValueError("Name should not be empty or only spaces.")

            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                sql = """
                    insert into mas_room (room_group_id, name) values(%s, %s);
                    ;
                """
                cur.execute(sql, (int(id), form_name),)
            conn.commit()
        except Exception as e:
            traceback.print_exc()
            conn.rollback()
            status_code = 500
            res["message"] = str(e)
        finally:
            conn.close()
        return jsonify(res), status_code
    
@app.route('/rooms/<int:id>/delete', methods=['POST'])
@login_required
def room_delete(id):  
    conn = getConnection()
    res, status_code = getInitialResponse()
    try:
        group_id = request.args.get("group_id");
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            sql = """
                delete from mas_room where id = %s;
                ;
            """
            cur.execute(sql, (int(id),))
        conn.commit()
    except Exception as e:
        traceback.print_exc()
        conn.rollback()
        status_code = 500
        res["message"] = str(e)
    finally:
        conn.close()
    return jsonify(res), status_code

@app.route('/rooms/<int:id>')
@login_required
def room_detail(id):
    room_group = {}
    room = {}
    conn = getConnection()
    group_id = request.args.get("group_id");
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        sql = """
            select name from mas_room_group
            where id = %s;
            ;
        """
        cur.execute(sql, (int(group_id),))
        room_group_list = cur.fetchall()
        if len(room_group_list) != 1:
            raise ValueError("group name count is not one. group_id={0}".format(group_id))
        room_group['name'] = room_group_list[0]['name'];
        room_group['id'] = group_id
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        sql = """
            select id, name from mas_room
            where id = %s
            ;
        """
        cur.execute(sql, (int(id),))
        room_list = cur.fetchall()
        if len(room_list) != 1:
            raise ValueError("room count is not one. id={0}".format(id))
        room['name'] = room_list[0]['name'];
        room['id'] = id
    
    conn.close()
    return render_template('testapp/room_detail.html', room=room, room_group=room_group)

@app.route('/rooms/<int:id>/update', methods=['POST'])
@login_required
def room_update(id):
    conn = getConnection()
    res, status_code = getInitialResponse()
    try:
        group_id = request.args.get("group_id");
        form_name = request.form.get('name')
        if form_name is None:
            raise ValueError("name is null!")
        form_name = str.strip(form_name)
        if not form_name:
            raise ValueError("Name should not be empty or only spaces.")
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            sql = """
                update mas_room
                SET name = %s
                where id = %s;
                ;
            """
            cur.execute(sql, (form_name, int(id)),)
        conn.commit()
    except Exception as e:
        traceback.print_exc()
        conn.rollback()
        status_code = 500
        res["message"] = str(e)
    finally:
        conn.close()
    return jsonify(res), status_code

@app.route('/room_groups_rsv')
@login_required
def room_group_list_rsv():
    conn = getConnection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        sql = """
            select mas_room_group.id as id, mas_room_group.name as name, count(mas_room.id) as room_count from mas_room_group
            left outer join mas_room on mas_room_group.id = mas_room.room_group_id 
            group by mas_room_group.id
            having 0 < room_count
            order by mas_room_group.name;
            ;
        """
        cur.execute(sql)
        room_group_list = cur.fetchall()
    conn.close()
    return render_template('testapp/room_group_list_rsv.html', room_group_list=room_group_list)

@app.route('/schedule/<int:group_id>')
@login_required
def schedule(group_id):
    room_group = {}
    meeting_list = {}

    view = request.args.get("view");
    date = request.args.get("date");

    conn = getConnection()
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        sql = """
            select name from mas_room_group
            where id = %s;
            ;
        """
        cur.execute(sql, (int(group_id),))
        room_group_list = cur.fetchall()
        if len(room_group_list) != 1:
            raise ValueError("group name count is not one. group_id={0}".format(group_id))
        room_group['name'] = room_group_list[0]['name'];
        room_group['id'] = group_id
    
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        sql = """
            select id, name from mas_room
            where room_group_id = %s
            order by name;
            ;
        """
        cur.execute(sql, (int(group_id),))
        room_list = cur.fetchall()

    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        sql = """
            select trn_meeting.id as meeting_id, room_id, trn_meeting.user_id as user_id, trn_meeting.name as meeting_name,
              start_time, end_time, trn_meeting.comment as comment,
              mas_user.name as user_name, mas_user.public_id as user_public_id from trn_meeting
            join mas_room on trn_meeting.room_id = mas_room.id
            left outer join mas_user on trn_meeting.user_id = mas_user.id
            where mas_room.room_group_id = %s;
            ;
        """
        cur.execute(sql, (int(group_id),))
        meeting_list = cur.fetchall()
    conn.close()
    return render_template('testapp/schedule.html', room_group = room_group, room_list = room_list, meeting_list=meeting_list, view=view, date=date )

@app.route('/meetings/upsert', methods=['POST'])
@login_required
def meeting_upsert():
    conn = getConnection()
    res, status_code = getInitialResponse()
    try:
        group_id = request.args.get("group_id");

        room_id = request.form.get('room_id');
        user_id = request.form.get('user_id');
        meeting_id = request.form.get('meeting_id');
        meeting_name = request.form.get('meeting_name')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        comment = request.form.get('comment')
        
        with conn.cursor(pymysql.cursors.DictCursor) as cur:

            # Take a lock because it is assumed that the period overlap check
            # will not work if insert or update is executed at the same time.
            sql = """
                SELECT * FROM mas_room
                WHERE id = %s FOR UPDATE;
                ;
            """
            cur.execute(sql, (int(room_id)),)

            if not meeting_id:
                # Check if there are any meetings with overlapping periods.
                with conn.cursor(pymysql.cursors.DictCursor) as cur:
                    sql = """
                        SELECT COUNT(*) as cnt from trn_meeting
                        WHERE (room_id = %(roomId)s) AND 
                        (NOT (end_time <= %(startTime)s OR %(endTime)s <= start_time));
                        ;
                    """
                    cur.execute(sql, {"roomId": room_id, "startTime": start_time, "endTime": end_time},)
                    overlapCntRows = cur.fetchall()
    
                    if 0 < int(overlapCntRows[0]['cnt']):
                        raise ValueError("The specified period overlaps with another reservation.")
                with conn.cursor(pymysql.cursors.DictCursor) as cur:
                    sql = """
                        INSERT INTO trn_meeting (room_id, user_id, name, start_time, end_time, comment) 
                        VALUES(%s, %s, %s, %s, %s, %s);
                        ;
                    """
                    cur.execute(sql, (int(room_id), int(user_id), meeting_name, start_time, end_time, comment),)
            else:
                with conn.cursor(pymysql.cursors.DictCursor) as cur:
                    # Check if there are any meetings with overlapping periods.
                    sql = """
                        SELECT COUNT(*) as cnt from trn_meeting
                        WHERE (id <> %(meetingId)s) AND (room_id = %(roomId)s) AND 
                        (NOT (end_time <= %(startTime)s OR %(endTime)s <= start_time));
                        ;
                    """
                    cur.execute(sql, {"meetingId": meeting_id, "roomId": room_id, "startTime": start_time, "endTime": end_time},)
                    overlapCntRows = cur.fetchall()
    
                    if 0 < int(overlapCntRows[0]['cnt']):
                        raise ValueError("The specified period overlaps with another reservation.")
                with conn.cursor(pymysql.cursors.DictCursor) as cur:
                    sql = """
                        UPDATE trn_meeting 
                        SET name = %s, start_time = %s, end_time =%s, comment = %s
                        WHERE id = %s;
                        ;
                    """
                    cur.execute(sql, (meeting_name, start_time, end_time, comment, int(meeting_id)),)

        conn.commit()
    except Exception as e:
        app.logger.error(str(e))
        traceback.print_exc()
        conn.rollback()
        status_code = 500
        res["message"] = str(e)
    finally:
        conn.close()
    return jsonify(res), status_code

@app.route('/meetings/delete', methods=['POST'])
@login_required
def meeting_delete():
    conn = getConnection()
    res, status_code = getInitialResponse()
    try:
        group_id = request.args.get("group_id");

        meeting_id = request.form.get('meeting_id');

        if meeting_id is None:
            raise ValueError("meeting_id is None group_id={0}".format(group_id));
        
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            sql = """
                delete from trn_meeting 
                where id = %s;
                ;
            """
            cur.execute(sql, (int(meeting_id)),)
        conn.commit()
    except Exception as e:
        traceback.print_exc()
        conn.rollback()
        status_code = 500
        res["message"] = str(e)
    finally:
        conn.close()
    return jsonify(res), status_code
