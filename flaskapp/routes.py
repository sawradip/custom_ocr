import os
import shutil
import secrets
from glob import glob
from flask import render_template, url_for, flash, redirect, request
from flaskapp import app, db, bcrypt, ocr_tool, drive_tool, LOCAL_IMAGE_FOLDER
from flaskapp.models import User, Entry
from flaskapp.forms import RegistrationForm, LoginForm, UploadForm, SearchForm
from flask_login import login_user, current_user, logout_user, login_required
    
app.app_context().push()
db.create_all()

results = [
    {
        'user_id': 'Mr.Abul Kalam',
        'company_name': 'Hashem Group.Ltd',
        'report_text':r'bed sheet orange plant geaR hgtu',
        'date_posted': 'April 20, 2021',
        'report_img' : 'https://picsum.photos/200/200',
        'comments' : ''
    },
    {
        'user_id': 'Mr.Kbul Alam',
        'company_name': 'Kashem Steels.Ltd',
        'report_text':r'Shoe bed sheet sitting sofa\n ',
        'date_posted': 'May 20, 2021',
        'report_img' : 'https://picsum.photos/200/200',
        'comments' : ''
    },
]

@app.route("/search", methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        search_query = form.search_box.data.strip().lower()
        entries = Entry.query.filter(Entry.report_text.like(f"%{search_query.replace(' ', '%')}%")).all()
        report_img_folder = os.path.join(app.root_path, LOCAL_IMAGE_FOLDER)
        local_images = glob(os.path.join(report_img_folder, '*'))
        TEMP_FOLDER = os.path.join(app.root_path, 'static', 'report_pics', 'temp')

        if os.path.exists(TEMP_FOLDER):
            shutil.rmtree(TEMP_FOLDER)
        os.makedirs(TEMP_FOLDER)      

        
        result_entries = []
        for i, entry in enumerate(entries):

            if entry.report_img_name not in ' '.join(local_images):
                print(f'{i+1}/{len(entries)} {entry.report_img_name} Downloading...')
                drive_tool.download_file(image_name = entry.report_img_name, 
                                         image_drive_id = entry.report_img, 
                                         root_folder = report_img_folder)
                
            local_impath = os.path.join(report_img_folder, entry.report_img_name)
            ocr_tool.write_ocr_img(input_impath = local_impath,
                          output_dir = TEMP_FOLDER,
                          search_query = search_query,
                          text_str = entry.report_text,
                          positional_str = entry.report_positional_info)
            
            result = {}
            result['company_name'] = entry.company_name
            result['date_posted']=entry.date_posted
            result['comment']=entry.comment
            result['uploader'] = entry.uploader.username  
            result['img_path'] = glob(os.path.join(TEMP_FOLDER, '*'))[0].replace(app.root_path, '')
            #r'\temp\f6ce86bda4ccd964.jpeg'#local_impath.replace(app.root_pa')th, 
            # r'\stemp\f6ce86bda4ccd964.jpeg' 
            # local_impath.replace(app.root_path, '')
            # print(local_impath.replace(app.root_path, ''))
            # print(glob(os.path.join(TEMP_FOLDER, '*'))[0])
            # print(os.path.join(TEMP_FOLDER, entry.report_img_name).replace(app.root_path, ''))
            result_entries.append(result)

        return render_template('search.html', results = result_entries, form = form)
    return render_template('search.html',  form = form)

# @app.route("/login")
# def login():
#     return render_template('login.html')

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, LOCAL_IMAGE_FOLDER, picture_fn)

    form_picture.save(picture_path)
    # output_size = (125, 125)
    # i = Image.open(form_picture)
    # i.thumbnail(output_size)
    # i.save(picture_path)

    return picture_path


@app.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        picture_path = save_picture(form.report_img_file.data)
        text_str, positional_str = ocr_tool.get_info_str(picture_path)
        gdrive_image_id = drive_tool.upload_file(picture_path)

        picture_fn = os.path.split(picture_path)[-1]

        entry = Entry(company_name = form.company_name.data,
                      report_text = text_str,
                      report_positional_info = positional_str,
                      comment = form.comment.data,
                      report_img = gdrive_image_id,
                      report_img_name = picture_fn,
                      uploader = current_user)
        db.session.add(entry)
        db.session.commit()
        flash('This image entry has been uploaded!', 'success')
        return redirect(url_for('upload'))
    return render_template('upload.html', form=form)



@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('search'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        logout_user()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('search'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('search'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/account")
@login_required
def account():
    return render_template('account.html')