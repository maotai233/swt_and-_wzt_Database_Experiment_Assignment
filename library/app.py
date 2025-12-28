from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from functools import wraps
from datetime import datetime, timedelta
from flask import flash  
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, Response

app = Flask(__name__)
app.secret_key = 'library_management_system'

# ---------------- 数据库初始化 ----------------
def init_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # ===== 创建表 =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS publisher (
            PNo VARCHAR(20) PRIMARY KEY,
            PName VARCHAR(50) NOT NULL,
            PAddress VARCHAR(50)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS booktype (
            BTNo CHAR(10) PRIMARY KEY,
            BTName VARCHAR(50) NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book (
            BNo VARCHAR(20) PRIMARY KEY,
            BTNo CHAR(10),
            PNo VARCHAR(20),
            BName VARCHAR(50) NOT NULL,
            BAuthor VARCHAR(20),
            PTime DATETIME,
            Price NUMERIC(8,2),
            InputTime DATETIME,
            TotalNum INT,
            Biomass INT,
            FOREIGN KEY (BTNo) REFERENCES booktype(BTNo),
            FOREIGN KEY (PNo) REFERENCES publisher(PNo)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS manager (
            MNo VARCHAR(20) PRIMARY KEY,
            MName CHAR(10),
            MSex CHAR(4),
            MTNumber CHAR(11),
            MHAddress VARCHAR(50),
            MEducation VARCHAR(50)
        )
    ''')

    # 创建 reader 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reader (
            RNo VARCHAR(20) PRIMARY KEY,
            CNo CHAR(12),
            RName CHAR(8),
            RSex CHAR(4),
            RIDNum CHAR(24),
            RFine NUMERIC(8,2),
            username VARCHAR(50),
            password VARCHAR(100)
                   
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookcredit (
            CNo CHAR(12) PRIMARY KEY,
            RNo VARCHAR(20),
            CFine NUMERIC(8,2),
            CNum INT,
            CW CHAR(2),
            CDate DATETIME,
            Crenew DATETIME,
            FOREIGN KEY (RNo) REFERENCES reader(RNo)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrow (
            CNo CHAR(12),
            BNo VARCHAR(20),
            BBTime DATETIME,
            BBBTime DATETIME,
            BBFine NUMERIC(8,2),
            BBW CHAR(2),
            PRIMARY KEY (CNo, BNo),
            FOREIGN KEY (CNo) REFERENCES bookcredit(CNo),
            FOREIGN KEY (BNo) REFERENCES book(BNo)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookstocking (
            BBSNo VARCHAR(20) PRIMARY KEY,
            BBSTime DATETIME,
            BBSW CHAR(2),
            MNo VARCHAR(20),
            FOREIGN KEY (MNo) REFERENCES manager(MNo)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookStockingDetail (
            BBSNo VARCHAR(20),
            BNo VARCHAR(20),
            BBSNum INT,
            PRIMARY KEY (BBSNo, BNo),
            FOREIGN KEY (BBSNo) REFERENCES bookstocking(BBSNo),
            FOREIGN KEY (BNo) REFERENCES book(BNo)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS breakage (
            BANO VARCHAR(20) PRIMARY KEY,
            BADNo VARCHAR(20),
            BATime DATETIME,
            BASum INT,
            MNO VARCHAR(20),
            FOREIGN KEY (MNO) REFERENCES manager(MNo)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS breakageDetail (
            BADNo VARCHAR(20) PRIMARY KEY,
            BNo VARCHAR(20),
            Reasons CHAR(50),
            BADNum INT,
            FOREIGN KEY (BNo) REFERENCES book(BNo)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fine (
            FNo CHAR(18) PRIMARY KEY,
            CNo CHAR(12),
            FTime DATETIME,
            FFine NUMERIC(8,2),
            FOREIGN KEY (CNo) REFERENCES bookcredit(CNo)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fine_detail (
            FDNo VARCHAR(20) PRIMARY KEY,
            FNo CHAR(18),
            BNo VARCHAR(20),
            Reason VARCHAR(100),
            FineAmount NUMERIC(8,2),
            FOREIGN KEY (FNo) REFERENCES fine(FNo),
            FOREIGN KEY (BNo) REFERENCES book(BNo)
        )
    ''')

    conn.commit()

    # ===== 插入初始数据 =====
    try:
        # 图书类型
        cursor.execute("INSERT OR IGNORE INTO booktype VALUES ('H', '语言文字')")
        cursor.execute("INSERT OR IGNORE INTO booktype VALUES ('K', '历史地理')")
        cursor.execute("INSERT OR IGNORE INTO booktype VALUES ('I', '文学')")

        # 出版社
        cursor.execute("INSERT OR IGNORE INTO publisher VALUES ('P001', '湖南文艺出版社', '湖南')")
        cursor.execute("INSERT OR IGNORE INTO publisher VALUES ('P002', '人民文学出版社', '北京')")
        cursor.execute("INSERT OR IGNORE INTO publisher VALUES ('P003', '科学出版社', '北京')")

        # 管理员
        cursor.execute("INSERT OR IGNORE INTO manager VALUES ('M001', '吴管理员', '女', '13800138000', '深圳市', '本科')")
        cursor.execute("INSERT OR IGNORE INTO manager VALUES ('M002', '苏管理员', '女', '13900139000', '深圳市', '本科')")

        # 图书
        cursor.execute("INSERT OR IGNORE INTO book VALUES ('001', 'H', 'P001', '长安的荔枝', '马伯庸', '2025-12-25', 27.00, '2025-12-25', 10, 10)")
        cursor.execute("INSERT OR IGNORE INTO book VALUES ('002', 'H', 'P001', '鲜衣怒马少年时', '少年怒马', '2025-12-25', 35.00, '2025-12-25', 8, 8)")
        cursor.execute("INSERT OR IGNORE INTO book VALUES ('003', 'I', 'P002', '三体', '刘慈欣', '2025-12-25', 70.00, '2025-12-25', 5, 5)")
        cursor.execute("INSERT OR IGNORE INTO book VALUES ('004', 'K', 'P002', '历史地理学讲义', '史念海', '2025-12-28', 30.00, '2025-12-28', 5, 10)")
        
        # 读者数据
        # 先检查是否存在 R001
        cursor.execute("SELECT COUNT(*) FROM reader WHERE RNo = 'R001'")
        r001_exists = cursor.fetchone()[0] > 0
        
        if not r001_exists:
            # 插入新读者
            cursor.execute("INSERT INTO reader (RNo, CNo, RName, RSex, RIDNum, RFine, username, password) VALUES ('R001', 'C001', '小吴', '女', '110101199001011234', 0.0, 'reader001', 'reader123')")
        else:
            # 更新现有读者的用户名和密码
            cursor.execute("UPDATE reader SET username = 'reader001', password = 'reader123' WHERE RNo = 'R001'")
        
        # 检查 R002
        cursor.execute("SELECT COUNT(*) FROM reader WHERE RNo = 'R002'")
        r002_exists = cursor.fetchone()[0] > 0
        
        if not r002_exists:
            cursor.execute("INSERT INTO reader (RNo, CNo, RName, RSex, RIDNum, RFine, username, password) VALUES ('R002', 'C002', '小苏', '女', '110101199002021235', 0.0, 'reader002', 'reader123')")
        else:
            cursor.execute("UPDATE reader SET username = 'reader002', password = 'reader123' WHERE RNo = 'R002'")

        # 书卡
        cursor.execute("INSERT OR IGNORE INTO bookcredit VALUES ('C001', 'R001', 0.0, 5, '0', datetime('now'), datetime('now', '+1 year'))")
        cursor.execute("INSERT OR IGNORE INTO bookcredit VALUES ('C002', 'R002', 0.0, 5, '0', datetime('now'), datetime('now', '+1 year'))")

        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"数据插入完整性错误: {e}")
        # 继续执行，不中断
    except Exception as e:
        print(f"数据插入出错: {e}")
        # 继续执行，不中断
    
    conn.close()
    print("数据库初始化完成")

# ---------------- 同步罚款数据函数 ----------------
def sync_fine_data(card_number):
    """同步罚款数据，确保 fine 表和 reader 表数据一致"""
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 计算 fine 表中的总未缴罚款
        cursor.execute('SELECT SUM(FFine) FROM fine WHERE CNo = ? AND FFine > 0', (card_number,))
        fine_total = cursor.fetchone()
        total_fine = float(fine_total[0]) if fine_total and fine_total[0] else 0.0
        
        # 获取读者ID
        cursor.execute('SELECT RNo FROM reader WHERE CNo = ?', (card_number,))
        reader_result = cursor.fetchone()
        
        if reader_result:
            reader_id = reader_result[0]
            # 更新 reader 表
            cursor.execute('UPDATE reader SET RFine = ? WHERE RNo = ?', (total_fine, reader_id))
            # 更新 bookcredit 表
            cursor.execute('UPDATE bookcredit SET CFine = ? WHERE CNo = ?', (total_fine, card_number))
        
        conn.commit()
        conn.close()
        
        return total_fine
    except Exception as e:
        print(f"同步罚款数据出错: {e}")
        import traceback
        traceback.print_exc()
        return 0.0

# ---------------- 创建视图 ----------------
def create_views():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS 入库单 AS
        SELECT
            bs.BBSNo as 入库单编号,
            bs.BBSTime as 入库日期,
            m.MName as 经手人姓名,
            bs.BBSW as 是否已入库,
            bsd.BNo as 图书编号,
            b.BName as 书名,
            p.PName as 出版社名,
            bsd.BBSNum as 入库数量
        FROM bookstocking bs
        JOIN bookStockingDetail bsd ON bs.BBSNo = bsd.BBSNo
        JOIN manager m ON bs.MNo = m.MNo
        JOIN book b ON bsd.BNo = b.BNo
        JOIN publisher p ON b.PNo = p.PNo
    ''')
    conn.commit()
    conn.close()


# ---------------- 创建触发器 ----------------
def create_triggers():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS check_stocking_status
        BEFORE DELETE ON bookStockingDetail
        FOR EACH ROW
        BEGIN
            SELECT CASE
                WHEN (SELECT BBSW FROM bookStocking WHERE BBSNo = OLD.BBSNo) = '1'
                THEN RAISE(ABORT, '已入库不能删除！')
            END;
        END;
    ''')
    conn.commit()
    conn.close()


# ---------------- 登录装饰器 ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ---------------- 路由 ----------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        if user_type == 'admin' and username == 'admin' and password == 'admin123':
            session['user_type'] = 'admin'
            session['username'] = username
            session['user_id'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        elif user_type == 'reader':
            # 从数据库验证读者
            conn = sqlite3.connect('library.db')
            cursor = conn.cursor()
            cursor.execute('SELECT RNo, RName FROM reader WHERE username = ? AND password = ?', (username, password))
            reader = cursor.fetchone()
            conn.close()
            
            if reader:
                session['user_type'] = 'reader'
                session['username'] = reader[1]  # RName
                session['user_id'] = reader[0]   # RNo
                return redirect(url_for('reader_dashboard'))
            else:
                return render_template('login.html', error='用户名或密码错误')
        else:
            return render_template('login.html', error='用户名或密码错误')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    # 初始化统计数据
    stats = {
        'total_books': 0,
        'total_readers': 0,
        'active_borrows': 0,
        'overdue_books': 0
    }
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 查询图书总数
        cursor.execute('SELECT COUNT(*) FROM book')
        stats['total_books'] = cursor.fetchone()[0] or 0
        
        # 查询读者总数
        cursor.execute('SELECT COUNT(*) FROM reader')
        stats['total_readers'] = cursor.fetchone()[0] or 0
        
        # 查询在借图书数（在borrow表中BBBTime[还书时间]为空的记录）
        cursor.execute('SELECT COUNT(*) FROM borrow WHERE BBBTime IS NULL OR BBBTime = ""')
        stats['active_borrows'] = cursor.fetchone()[0] or 0
        
        # 查询逾期图书数：借出超过30天且未还的
        cursor.execute("""
            SELECT COUNT(*) FROM borrow 
            WHERE (BBBTime IS NULL OR BBBTime = "") 
            AND julianday('now') - julianday(BBTime) > 30
        """)
        stats['overdue_books'] = cursor.fetchone()[0] or 0
        
        conn.close()
    except Exception as e:
        print(f"查询统计信息出错: {e}")
        # 出错时使用默认值
    
    # 获取用户名
    username = session.get('username', '管理员')
    
    return render_template('admin_dashboard.html', 
                         username=username,
                         stats=stats)

# 管理员仪表盘图表数据API
@app.route('/api/admin/dashboard/charts')
@login_required
def admin_dashboard_charts():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 月度借阅统计（最近6个月）
        monthly_data = [0] * 6
        month_labels = []
        try:
            cursor.execute('''
                SELECT strftime('%Y-%m', BBTime) as month, COUNT(*) as count
                FROM borrow
                WHERE BBTime >= date('now', '-6 months')
                GROUP BY strftime('%Y-%m', BBTime)
                ORDER BY month
            ''')
            monthly_stats = cursor.fetchall()
            
            # 生成最近6个月的月份名称
            import calendar
            from datetime import datetime, timedelta
            
            current_date = datetime.now()
            for i in range(5, -1, -1):
                # 计算前i个月的日期
                month_date = current_date - timedelta(days=30*i)
                month_str = month_date.strftime('%Y-%m')
                month_name = f"{month_date.month}月"
                month_labels.append(month_name)
                
                # 查找对应月份的数据
                for stat in monthly_stats:
                    if stat[0] == month_str:
                        monthly_data[5-i] = stat[1]
                        break
        except Exception as e:
            print(f"查询月度统计出错: {e}")
            month_labels = ['1月', '2月', '3月', '4月', '5月', '6月']
        
        # 借阅时间段统计
        time_data = [0, 0, 0]  # 上午、下午、晚上
        try:
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN CAST(strftime('%H', BBTime) AS INTEGER) BETWEEN 8 AND 12 THEN '上午'
                        WHEN CAST(strftime('%H', BBTime) AS INTEGER) BETWEEN 14 AND 18 THEN '下午'
                        WHEN CAST(strftime('%H', BBTime) AS INTEGER) BETWEEN 19 AND 22 THEN '晚上'
                    END as time_period,
                    COUNT(*) as count
                FROM borrow
                WHERE BBTime IS NOT NULL
                AND (CAST(strftime('%H', BBTime) AS INTEGER) BETWEEN 8 AND 12 
                     OR CAST(strftime('%H', BBTime) AS INTEGER) BETWEEN 14 AND 18
                     OR CAST(strftime('%H', BBTime) AS INTEGER) BETWEEN 19 AND 22)
                GROUP BY time_period
                ORDER BY 
                    CASE time_period
                        WHEN '上午' THEN 1
                        WHEN '下午' THEN 2
                        WHEN '晚上' THEN 3
                    END
            ''')
            
            time_stats = cursor.fetchall()
            
            for stat in time_stats:
                if stat[0] == '上午':
                    time_data[0] = stat[1]
                elif stat[0] == '下午':
                    time_data[1] = stat[1]
                elif stat[0] == '晚上':
                    time_data[2] = stat[1]
        except Exception as e:
            print(f"查询时间段统计出错: {e}")
        
        # 今日借阅统计
        try:
            cursor.execute('''
                SELECT COUNT(*) FROM borrow 
                WHERE DATE(BBTime) = DATE('now')
            ''')
            today_borrows = cursor.fetchone()[0] or 0
        except Exception as e:
            print(f"查询今日借阅出错: {e}")
            today_borrows = 0
        
        # 本周借阅统计
        try:
            cursor.execute('''
                SELECT COUNT(*) FROM borrow 
                WHERE strftime('%W', BBTime) = strftime('%W', 'now')
                AND strftime('%Y', BBTime) = strftime('%Y', 'now')
            ''')
            week_borrows = cursor.fetchone()[0] or 0
        except Exception as e:
            print(f"查询本周借阅出错: {e}")
            week_borrows = 0
        
        conn.close()
        
        return jsonify({
            'success': True,
            'monthly_labels': month_labels,
            'monthly_data': monthly_data,
            'time_data': time_data,
            'today_borrows': today_borrows,
            'week_borrows': week_borrows
        })
        
    except Exception as e:
        print(f"获取仪表盘图表数据出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'获取数据失败: {str(e)}'}), 500

# reader_dashboard 路由
@app.route('/reader/dashboard')
@login_required
def reader_dashboard():
    if session.get('user_type') != 'reader':
        return redirect(url_for('login'))
    
    try:
        reader_id = session.get('user_id')
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 查询读者信息
        cursor.execute('''
            SELECT r.RNo, r.CNo, r.RName, r.RFine,
                   bc.CNum, bc.CW, bc.Crenew,
                   (SELECT COUNT(*) FROM borrow WHERE CNo = r.CNo AND (BBBTime IS NULL OR BBBTime = '')) as borrowed_count
            FROM reader r
            LEFT JOIN bookcredit bc ON r.CNo = bc.CNo
            WHERE r.RNo = ?
        ''', (reader_id,))
        
        reader = cursor.fetchone()
        
        if reader:
            reader_info = {
                'reader_number': reader[0],
                'card_number': reader[1],
                'reader_name': reader[2],
                'unpaid_fine': float(reader[3] or 0),
                'max_books': reader[4] if reader[4] else 5,
                'borrowed_books': reader[7] or 0,
                'card_status': '正常' if reader[5] == '0' else '挂失',
                'renew_date': reader[6]
            }
        else:
            # 如果没有读者记录，使用默认值
            reader_info = {
                'reader_number': reader_id,
                'card_number': 'C001',
                'reader_name': session.get('username', '读者'),
                'unpaid_fine': 0.0,
                'max_books': 5,
                'borrowed_books': 0,
                'card_status': '正常',
                'renew_date': datetime.now().strftime('%Y-%m-%d')
            }
        
        # 查询最近的借阅记录
        if reader_info['card_number']:
            cursor.execute('''
                SELECT b.BNo, bk.BName, b.BBTime, 
                       DATE(b.BBTime, '+30 days') as DueDate,
                       CASE 
                           WHEN b.BBBTime IS NULL OR b.BBBTime = '' THEN '在借'
                           ELSE '已还'
                       END as status
                FROM borrow b
                JOIN book bk ON b.BNo = bk.BNo
                WHERE b.CNo = ?
                ORDER BY b.BBTime DESC
                LIMIT 5
            ''', (reader_info['card_number'],))
            
            recent_borrows = cursor.fetchall()
        else:
            recent_borrows = []
        
        conn.close()
        
        return render_template('reader_dashboard.html', 
                              username=session.get('username', '读者'),
                              reader_info=reader_info,
                              recent_borrows=recent_borrows)
        
    except Exception as e:
        print(f"加载读者仪表板出错: {e}")
        # 出错时返回基本页面
        return render_template('reader_dashboard.html', 
                              username=session.get('username', '读者'),
                              reader_info={
                                  'reader_number': session.get('user_id', 'R001'),
                                  'card_number': 'C001',
                                  'reader_name': session.get('username', '读者'),
                                  'unpaid_fine': 0.0,
                                  'max_books': 5,
                                  'borrowed_books': 0,
                                  'card_status': '正常',
                                  'renew_date': datetime.now().strftime('%Y-%m-%d')
                              },
                              recent_borrows=[])

# 读者管理路由
@app.route('/admin/readers')
@login_required
def admin_readers():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # 查询所有读者
    cursor.execute('''
        SELECT r.RNo, r.CNo, r.RName, r.RSex, r.RIDNum, r.RFine, 
               bc.CNum, bc.CW, bc.CDate, bc.Crenew
        FROM reader r
        LEFT JOIN bookcredit bc ON r.CNo = bc.CNo
    ''')
    readers_data = cursor.fetchall()
    
    # 处理数据
    readers = []
    for reader in readers_data:
        # 计算已借册数
        cursor.execute('SELECT COUNT(*) FROM borrow WHERE CNo = ? AND BBBTime IS NULL', (reader[1],))
        borrowed_count = cursor.fetchone()[0] or 0
        
        readers.append({
            'reader_number': reader[0],
            'card_number': reader[1],
            'reader_name': reader[2],
            'sex': reader[3],
            'id_number': reader[4],
            'unpaid_fine': reader[5],
            'borrowable_books': reader[6] if reader[6] else 5,  # 默认5本
            'borrowed_books': borrowed_count,
            'is_lost': reader[7] == '1' if reader[7] else False,  # CW=1表示挂失
            'card_date': reader[8],
            'renew_date': reader[9],
        })
    
    # 统计信息
    cursor.execute('SELECT COUNT(*) FROM reader')
    total_readers = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM bookcredit WHERE CW = "1"')
    lost_cards = cursor.fetchone()[0]
    
    stats = {
        'total_cards': total_readers,
        'active_cards': total_readers - lost_cards,
        'lost_cards': lost_cards
    }
    
    conn.close()
    
    return render_template('readers.html', readers=readers, stats=stats)

# 借阅管理路由
@app.route('/admin/borrows')
@login_required
def admin_borrows():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # 查询当前借阅记录
    cursor.execute('''
        SELECT b.CNo, b.BNo, bk.BName, r.RName, b.BBTime, 
               b.BBBTime, b.BBFine, b.BBW,
               DATE(b.BBTime, '+30 days') as DueDate
        FROM borrow b
        JOIN book bk ON b.BNo = bk.BNo
        JOIN bookcredit bc ON b.CNo = bc.CNo
        JOIN reader r ON bc.RNo = r.RNo
        WHERE b.BBBTime IS NULL OR b.BBBTime = ''
    ''')
    
    current_borrows = []
    for borrow in cursor.fetchall():
        # 计算是否逾期
        is_overdue = False
        if borrow[4]:  # 如果有借书时间
            cursor.execute('SELECT julianday("now") - julianday(?)', (borrow[4],))
            days_borrowed = cursor.fetchone()[0]
            is_overdue = days_borrowed > 30 if days_borrowed else False
        
        current_borrows.append({
            'card_number': borrow[0],
            'book_number': borrow[1],
            'book_name': borrow[2],
            'reader_name': borrow[3],
            'borrow_date': borrow[4],
            'return_date': borrow[5],
            'fine': borrow[6],
            'status': borrow[7],
            'due_date': borrow[8],
            'is_renewed': borrow[7] == '1',  # BBW=1表示已续借
            'is_overdue': is_overdue
        })
    
    conn.close()
    
    return render_template('borrow_manage.html', current_borrows=current_borrows)

# ================ 图书入库管理 ================
# 图书入库页面
@app.route('/admin/stock')
@login_required
def admin_stock():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 查询入库记录
        cursor.execute('''
            SELECT bs.BBSNo as 入库单编号,
                   bs.BBSTime as 入库日期,
                   m.MName as 经手人,
                   bs.BBSW as 是否已入库,
                   bsd.BNo as 图书编号,
                   b.BName as 书名,
                   p.PName as 出版社,
                   bsd.BBSNum as 入库数量
            FROM bookstocking bs
            LEFT JOIN bookStockingDetail bsd ON bs.BBSNo = bsd.BBSNo
            LEFT JOIN manager m ON bs.MNo = m.MNo
            LEFT JOIN book b ON bsd.BNo = b.BNo
            LEFT JOIN publisher p ON b.PNo = p.PNo
            ORDER BY bs.BBSTime DESC
        ''')
        stockings = cursor.fetchall()
        
        # 查询所有图书供选择
        cursor.execute('SELECT BNo, BName FROM book ORDER BY BName')
        books = cursor.fetchall()
        
        # 查询管理员
        cursor.execute('SELECT MNo, MName FROM manager')
        managers = cursor.fetchall()
        
        conn.close()
        
        return render_template('stock.html', 
                             stockings=stockings, 
                             books=books,
                             managers=managers)
        
    except Exception as e:
        print(f"加载入库页面出错: {e}")
        import traceback
        traceback.print_exc()
        flash('加载入库页面失败', 'error')
        return redirect(url_for('admin_dashboard'))

# 保存入库记录API
@app.route('/api/stock', methods=['POST'])
@login_required
def save_stock():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        data = request.json
        
        stock_no = data.get('stock_no')
        stock_date = data.get('stock_date')
        book_no = data.get('book_no')
        stock_num = int(data.get('stock_num', 0))
        
        print(f"[DEBUG] 入库数据: {data}")
        
        # 验证数据
        if not all([stock_no, stock_date, book_no]):
            return jsonify({'success': False, 'message': '请填写完整入库信息'}), 400
        
        if stock_num <= 0:
            return jsonify({'success': False, 'message': '入库数量必须大于0'}), 400
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 1. 检查入库单号是否已存在
        cursor.execute('SELECT COUNT(*) FROM bookstocking WHERE BBSNo = ?', (stock_no,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return jsonify({'success': False, 'message': '入库单号已存在'}), 400
        
        # 2. 检查图书是否存在
        cursor.execute('SELECT BNo, BName FROM book WHERE BNo = ?', (book_no,))
        book_info = cursor.fetchone()
        if not book_info:
            conn.close()
            return jsonify({'success': False, 'message': '图书不存在'}), 400
        
        # 3. 获取当前管理员（默认使用第一个管理员）
        cursor.execute('SELECT MNo FROM manager LIMIT 1')
        manager_result = cursor.fetchone()
        if manager_result:
            manager_no = manager_result[0]
        else:
            manager_no = 'M001'  # 默认值
        
        # 4. 创建入库单
        cursor.execute('''
            INSERT INTO bookstocking (BBSNo, BBSTime, BBSW, MNo)
            VALUES (?, ?, '1', ?)
        ''', (stock_no, stock_date, manager_no))
        
        # 5. 添加入库明细
        cursor.execute('''
            INSERT INTO bookStockingDetail (BBSNo, BNo, BBSNum)
            VALUES (?, ?, ?)
        ''', (stock_no, book_no, stock_num))
        
        # 6. 更新图书库存
        cursor.execute('''
            UPDATE book 
            SET TotalNum = TotalNum + ?, Biomass = Biomass + ?
            WHERE BNo = ?
        ''', (stock_num, stock_num, book_no))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'入库成功！图书《{book_info[1]}》入库{stock_num}本',
            'stock_no': stock_no
        })
        
    except sqlite3.IntegrityError as e:
        print(f"[ERROR] 数据库完整性错误: {e}")
        return jsonify({'success': False, 'message': '数据库完整性错误，可能入库单号已存在'}), 400
    except Exception as e:
        print(f"[ERROR] 入库出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'入库失败：{str(e)}'}), 500

# 获取入库记录列表API
@app.route('/api/stock/list')
@login_required
def get_stock_list():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bs.BBSNo as stock_no,
                   bs.BBSTime as stock_date,
                   m.MName as manager_name,
                   bs.BBSW as status,
                   bsd.BNo as book_no,
                   b.BName as book_name,
                   p.PName as publisher_name,
                   bsd.BBSNum as quantity
            FROM bookstocking bs
            LEFT JOIN bookStockingDetail bsd ON bs.BBSNo = bsd.BBSNo
            LEFT JOIN manager m ON bs.MNo = m.MNo
            LEFT JOIN book b ON bsd.BNo = b.BNo
            LEFT JOIN publisher p ON b.PNo = p.PNo
            ORDER BY bs.BBSTime DESC
        ''')
        
        stockings = cursor.fetchall()
        conn.close()
        
        results = []
        for stocking in stockings:
            results.append({
                'stock_no': stocking[0],
                'stock_date': stocking[1],
                'manager_name': stocking[2],
                'status': '已入库' if stocking[3] == '1' else '未入库',
                'book_no': stocking[4],
                'book_name': stocking[5],
                'publisher_name': stocking[6],
                'quantity': stocking[7]
            })
        
        return jsonify({'success': True, 'stockings': results})
        
    except Exception as e:
        print(f"[ERROR] 获取入库记录出错: {e}")
        return jsonify({'success': False, 'message': f'获取记录失败：{str(e)}'}), 500


# ================ 报损管理 ================
# 报损管理页面
@app.route('/admin/damage')
@login_required
def admin_damage():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 查询报损记录
        cursor.execute('''
            SELECT b.BANO, b.BADNo, b.BATime, b.BASum, m.MName,
                   bd.BNo, bk.BName, bd.Reasons, bd.BADNum
            FROM breakage b
            LEFT JOIN breakageDetail bd ON b.BADNo = bd.BADNo
            LEFT JOIN book bk ON bd.BNo = bk.BNo
            LEFT JOIN manager m ON b.MNO = m.MNo
            ORDER BY b.BATime DESC
        ''')
        
        damages = cursor.fetchall()
        conn.close()
        
        return render_template('damage.html', damages=damages)
        
    except Exception as e:
        print(f"加载报损页面出错: {e}")
        import traceback
        traceback.print_exc()
        flash('加载报损页面失败', 'error')
        return redirect(url_for('admin_dashboard'))

# 图书搜索API
@app.route('/api/books/search')
@login_required
def search_books_api():
    search_value = request.args.get('q', '')
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        if search_value:
            cursor.execute('''
                SELECT BNo, BName, BAuthor, Biomass
                FROM book 
                WHERE BNo LIKE ? OR BName LIKE ?
                ORDER BY BName
                LIMIT 20
            ''', (f'%{search_value}%', f'%{search_value}%'))
        else:
            cursor.execute('''
                SELECT BNo, BName, BAuthor, Biomass
                FROM book 
                ORDER BY BName
                LIMIT 20
            ''')
        
        books = cursor.fetchall()
        conn.close()
        
        books_list = []
        for book in books:
            books_list.append({
                'BNo': book[0],
                'BName': book[1],
                'BAuthor': book[2],
                'Biomass': book[3]
            })
        
        return jsonify({'success': True, 'books': books_list})
        
    except Exception as e:
        print(f"搜索图书出错: {e}")
        return jsonify({'success': False, 'message': f'搜索失败: {str(e)}'}), 500

# 保存报损记录API
@app.route('/api/damage', methods=['POST'])
@login_required
def save_damage():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        data = request.json
        
        damage_no = data.get('damage_no')
        damage_date = data.get('damage_date')
        book_no = data.get('book_no')
        damage_num = int(data.get('damage_num', 0))
        damage_reason = data.get('damage_reason')
        damage_remark = data.get('damage_remark', '')
        
        print(f"[DEBUG] 报损数据: {data}")
        
        # 验证数据
        if not all([damage_no, damage_date, book_no, damage_reason]):
            return jsonify({'success': False, 'message': '请填写完整报损信息'}), 400
        
        if damage_num <= 0:
            return jsonify({'success': False, 'message': '报损数量必须大于0'}), 400
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 1. 检查报损单号是否已存在
        cursor.execute('SELECT COUNT(*) FROM breakage WHERE BANO = ?', (damage_no,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return jsonify({'success': False, 'message': '报损单号已存在'}), 400
        
        # 2. 检查图书是否存在
        cursor.execute('SELECT BNo, BName, Biomass FROM book WHERE BNo = ?', (book_no,))
        book_info = cursor.fetchone()
        if not book_info:
            conn.close()
            return jsonify({'success': False, 'message': '图书不存在'}), 400
        
        # 3. 检查图书库存是否充足
        if book_info[2] < damage_num:
            conn.close()
            return jsonify({'success': False, 'message': f'图书库存不足，当前库存：{book_info[2]}本'}), 400
        
        # 4. 获取当前管理员（默认使用第一个管理员）
        cursor.execute('SELECT MNo FROM manager LIMIT 1')
        manager_result = cursor.fetchone()
        if manager_result:
            manager_no = manager_result[0]
        else:
            manager_no = 'M001'  # 默认值
        
        # 5. 生成报损明细单号
        cursor.execute('SELECT MAX(CAST(SUBSTR(BADNo, 3) AS INTEGER)) FROM breakageDetail WHERE BADNo LIKE "BD%"')
        result = cursor.fetchone()
        if result and result[0]:
            max_badno = result[0]
            bad_no = f"BD{max_badno + 1:03d}"
        else:
            bad_no = "BD001"
        
        # 6. 创建报损主记录
        cursor.execute('''
            INSERT INTO breakage (BANO, BADNo, BATime, BASum, MNO)
            VALUES (?, ?, ?, ?, ?)
        ''', (damage_no, bad_no, damage_date, damage_num, manager_no))
        
        # 7. 创建报损明细记录
        cursor.execute('''
            INSERT INTO breakageDetail (BADNo, BNo, Reasons, BADNum)
            VALUES (?, ?, ?, ?)
        ''', (bad_no, book_no, damage_reason, damage_num))
        
        # 8. 更新图书库存
        cursor.execute('''
            UPDATE book 
            SET Biomass = Biomass - ?
            WHERE BNo = ?
        ''', (damage_num, book_no))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'报损成功！图书《{book_info[1]}》报损{damage_num}本',
            'damage_no': damage_no
        })
        
    except sqlite3.IntegrityError as e:
        print(f"[ERROR] 数据库完整性错误: {e}")
        return jsonify({'success': False, 'message': '数据库完整性错误，可能报损单号已存在'}), 400
    except Exception as e:
        print(f"[ERROR] 报损出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'报损失败：{str(e)}'}), 500

# 删除报损记录API
@app.route('/api/damage/<damage_no>', methods=['DELETE'])
@login_required
def delete_damage(damage_no):
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 获取报损详情
        cursor.execute('''
            SELECT bd.BNo, bd.BADNum 
            FROM breakage b
            JOIN breakageDetail bd ON b.BADNo = bd.BADNo
            WHERE b.BANO = ?
        ''', (damage_no,))
        
        damage_info = cursor.fetchone()
        
        if not damage_info:
            conn.close()
            return jsonify({'success': False, 'message': '报损记录不存在'}), 404
        
        book_no = damage_info[0]
        damage_num = damage_info[1]
        
        # 恢复图书库存
        cursor.execute('UPDATE book SET Biomass = Biomass + ? WHERE BNo = ?', 
                      (damage_num, book_no))
        
        # 删除报损明细
        cursor.execute('DELETE FROM breakageDetail WHERE BADNo IN (SELECT BADNo FROM breakage WHERE BANO = ?)', 
                      (damage_no,))
        
        # 删除报损主记录
        cursor.execute('DELETE FROM breakage WHERE BANO = ?', (damage_no,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '报损记录删除成功'})
        
    except Exception as e:
        print(f"[ERROR] 删除报损记录出错: {e}")
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'}), 500

# ================ 查询统计功能 ================
# 查询统计页面
@app.route('/admin/reports')
@login_required
def admin_reports():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 基础统计信息
        try:
            cursor.execute('SELECT COUNT(*) FROM book')
            total_books = cursor.fetchone()[0] or 0
        except Exception as e:
            print(f"查询图书总数出错: {e}")
            total_books = 0
        
        try:
            cursor.execute('SELECT COUNT(*) FROM reader')
            total_readers = cursor.fetchone()[0] or 0
        except Exception as e:
            print(f"查询读者总数出错: {e}")
            total_readers = 0
        
        try:
            cursor.execute('SELECT COUNT(*) FROM borrow WHERE BBBTime IS NULL')
            active_borrows = cursor.fetchone()[0] or 0
        except Exception as e:
            print(f"查询在借图书出错: {e}")
            active_borrows = 0
        
        try:
            cursor.execute('''
                SELECT COUNT(*) FROM borrow 
                WHERE BBBTime IS NULL 
                AND julianday("now") - julianday(BBTime) > 30
            ''')
            overdue_books = cursor.fetchone()[0] or 0
        except Exception as e:
            print(f"查询逾期图书出错: {e}")
            overdue_books = 0
        
        # 月度借阅统计（最近6个月）
        monthly_data = [0] * 12
        try:
            cursor.execute('''
                SELECT strftime('%Y-%m', BBTime) as month, COUNT(*) as count
                FROM borrow
                WHERE BBTime >= date('now', '-6 months')
                GROUP BY strftime('%Y-%m', BBTime)
                ORDER BY month
            ''')
            monthly_stats = cursor.fetchall()
            
            # 生成12个月的完整数据
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            for i in range(12):
                month_num = ((current_month - 1 - i) % 12) + 1
                year = current_year if month_num <= current_month else current_year - 1
                month_str = f"{year}-{month_num:02d}"
                
                # 查找对应月份的数据
                for stat in monthly_stats:
                    if stat[0] == month_str:
                        monthly_data[11-i] = stat[1]
                        break
        except Exception as e:
            print(f"查询月度统计出错: {e}")
        
        # 热门图书排行
        popular_books = []
        try:
            cursor.execute('''
                SELECT b.BName, b.BAuthor, COUNT(*) as borrow_count
                FROM borrow bw
                JOIN book b ON bw.BNo = b.BNo
                GROUP BY bw.BNo
                ORDER BY borrow_count DESC
                LIMIT 10
            ''')
            popular_books = cursor.fetchall()
        except Exception as e:
            print(f"查询热门图书出错: {e}")
        
        # 图书分类统计
        book_type_stats = []
        try:
            cursor.execute('''
                SELECT bt.BTName, COUNT(b.BNo) as book_count,
                       ROUND(COUNT(b.BNo) * 100.0 / (SELECT COUNT(*) FROM book), 1) as percentage
                FROM booktype bt
                LEFT JOIN book b ON bt.BTNo = b.BTNo
                GROUP BY bt.BTNo
                ORDER BY book_count DESC
            ''')
            book_type_stats = cursor.fetchall()
        except Exception as e:
            print(f"查询图书分类统计出错: {e}")
        
        # 借阅时间段统计：
        time_labels = []
        time_data = []
        try:
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN CAST(strftime('%H', BBTime) AS INTEGER) BETWEEN 6 AND 12 THEN '上午 (6-12点)'
                        WHEN CAST(strftime('%H', BBTime) AS INTEGER) BETWEEN 12 AND 18 THEN '下午 (12-18点)'
                        WHEN CAST(strftime('%H', BBTime) AS INTEGER) BETWEEN 18 AND 24 THEN '晚上 (18-24点)'
                        ELSE '其他时间'
                    END as time_period,
                    COUNT(*) as count
                FROM borrow
                WHERE BBTime IS NOT NULL
                GROUP BY time_period
                ORDER BY 
                    CASE time_period
                        WHEN '上午 (6-12点)' THEN 1
                        WHEN '下午 (12-18点)' THEN 2
                        WHEN '晚上 (18-24点)' THEN 3
                        ELSE 4
                    END
            ''')
            
            time_stats = cursor.fetchall()
            
            # 转换为图表数据格式
            for stat in time_stats:
                time_labels.append(stat[0])
                time_data.append(stat[1])
        except Exception as e:
            print(f"查询时间段统计出错: {e}")
            # 使用默认值
            time_labels = ['上午 (6-12点)', '下午 (12-18点)', '晚上 (18-24点)']
            time_data = [0, 0, 0]
        
        conn.close()
        
        reports = {
            'total_books': total_books,
            'total_readers': total_readers,
            'active_borrows': active_borrows,
            'overdue_books': overdue_books,
            'monthly_data': monthly_data,
            'popular_books': popular_books,
            'book_type_stats': book_type_stats,
            'time_labels': time_labels,  
            'time_data': time_data       
        }
        
        return render_template('reports.html', **reports)
        
    except Exception as e:
        print(f"加载统计页面出错: {e}")
        import traceback
        traceback.print_exc()
        flash('加载统计页面失败', 'error')
        return redirect(url_for('admin_dashboard'))

# 图表数据API
@app.route('/api/reports/chart-data')
@login_required
def get_chart_data():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 月度借阅统计
        monthly_data = [0] * 12
        try:
            cursor.execute('''
                SELECT strftime('%m', BBTime) as month, COUNT(*) as count
                FROM borrow
                WHERE strftime('%Y', BBTime) = strftime('%Y', 'now')
                GROUP BY strftime('%m', BBTime)
                ORDER BY month
            ''')
            monthly_stats = cursor.fetchall()
            
            for stat in monthly_stats:
                month_index = int(stat[0]) - 1
                monthly_data[month_index] = stat[1]
        except Exception as e:
            print(f"获取月度统计出错: {e}")
        
        # 借阅时间段统计
        time_data = []
        try:
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN CAST(strftime('%H', BBTime) AS INTEGER) BETWEEN 6 AND 12 THEN '上午 (6-12点)'
                        WHEN CAST(strftime('%H', BBTime) AS INTEGER) BETWEEN 12 AND 18 THEN '下午 (12-18点)'
                        WHEN CAST(strftime('%H', BBTime) AS INTEGER) BETWEEN 18 AND 24 THEN '晚上 (18-24点)'
                        ELSE '其他时间'
                    END as time_period,
                    COUNT(*) as count
                FROM borrow
                WHERE BBTime IS NOT NULL
                GROUP BY time_period
                ORDER BY 
                    CASE time_period
                        WHEN '上午 (6-12点)' THEN 1
                        WHEN '下午 (12-18点)' THEN 2
                        WHEN '晚上 (18-24点)' THEN 3
                        ELSE 4
                    END
            ''')
            
            time_stats = cursor.fetchall()
            
            # 转换为数组格式
            for stat in time_stats:
                time_data.append(stat[1])
        except Exception as e:
            print(f"获取时间段统计出错: {e}")
            time_data = [0, 0, 0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'monthly_data': monthly_data,
            'time_data': time_data
        })
        
    except Exception as e:
        print(f"获取图表数据出错: {e}")
        return jsonify({'success': False, 'message': f'获取数据失败: {str(e)}'}), 500

# 导出借阅报表
@app.route('/api/reports/borrow')
@login_required
def export_borrow_report():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bw.BNo, b.BName, r.RName, bw.BBTime, bw.BBBTime, bw.BBFine,
                   CASE 
                       WHEN bw.BBBTime IS NULL THEN '在借'
                       ELSE '已还'
                   END as status
            FROM borrow bw
            JOIN book b ON bw.BNo = b.BNo
            JOIN bookcredit bc ON bw.CNo = bc.CNo
            JOIN reader r ON bc.RNo = r.RNo
            ORDER BY bw.BBTime DESC
        ''')
        
        borrows = cursor.fetchall()
        conn.close()
        
        # 生成CSV内容
        csv_content = "图书编号,书名,读者姓名,借书日期,还书日期,罚款金额,状态\n"
        for borrow in borrows:
            csv_content += f'{borrow[0]},"{borrow[1]}","{borrow[2]}",{borrow[3] or ""},{borrow[4] or ""},{borrow[5] or 0},{borrow[6]}\n'
        
        response = Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=borrow_report.csv"}
        )
        
        return response
        
    except Exception as e:
        print(f"导出借阅报表出错: {e}")
        return jsonify({'success': False, 'message': f'导出失败: {str(e)}'}), 500

# 导出图书报表
@app.route('/api/reports/books')
@login_required
def export_book_report():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT b.BNo, b.BName, b.BAuthor, bt.BTName, p.PName, 
                   b.Price, b.TotalNum, b.Biomass,
                   (SELECT COUNT(*) FROM borrow WHERE BNo = b.BNo) as borrow_count
            FROM book b
            LEFT JOIN booktype bt ON b.BTNo = bt.BTNo
            LEFT JOIN publisher p ON b.PNo = p.PNo
            ORDER BY b.BNo
        ''')
        
        books = cursor.fetchall()
        conn.close()
        
        # 生成CSV内容
        csv_content = "图书编号,书名,作者,类型,出版社,价格,总数量,现存量,借阅次数\n"
        for book in books:
            csv_content += f'{book[0]},"{book[1]}","{book[2]}","{book[3]}","{book[4]}",{book[5]},{book[6]},{book[7]},{book[8]}\n'
        
        response = Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=book_report.csv"}
        )
        
        return response
        
    except Exception as e:
        print(f"导出图书报表出错: {e}")
        return jsonify({'success': False, 'message': f'导出失败: {str(e)}'}), 500

# 导出读者报表
@app.route('/api/reports/readers')
@login_required
def export_reader_report():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.RNo, r.CNo, r.RName, r.RSex, r.RIDNum, r.RFine,
                   bc.CNum, bc.CW, bc.CDate,
                   (SELECT COUNT(*) FROM borrow WHERE CNo = r.CNo) as total_borrows
            FROM reader r
            LEFT JOIN bookcredit bc ON r.CNo = bc.CNo
            ORDER BY r.RNo
        ''')
        
        readers = cursor.fetchall()
        conn.close()
        
        # 生成CSV内容
        csv_content = "读者编号,借阅卡号,姓名,性别,身份证号,罚款金额,可借册数,卡状态,办卡日期,总借阅数\n"
        for reader in readers:
            status = "挂失" if reader[7] == '1' else "正常"
            csv_content += f'{reader[0]},{reader[1]},"{reader[2]}","{reader[3]}",{reader[4]},{reader[5]},{reader[6]},{status},{reader[8]},{reader[9]}\n'
        
        response = Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=reader_report.csv"}
        )
        
        return response
        
    except Exception as e:
        print(f"导出读者报表出错: {e}")
        return jsonify({'success': False, 'message': f'导出失败: {str(e)}'}), 500

@app.route('/admin/books')
@login_required
def admin_books():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))

    # 获取搜索参数
    search_type = request.args.get('search_type', '')
    search_value = request.args.get('search_value', '')
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # 构建基础查询
    query = '''
        SELECT b.BNo, b.BName, b.BAuthor, bt.BTName, p.PName, b.Price, b.TotalNum, b.Biomass
        FROM book b
        LEFT JOIN booktype bt ON b.BTNo = bt.BTNo
        LEFT JOIN publisher p ON b.PNo = p.PNo
    '''
    
    # 如果有搜索参数，添加WHERE条件
    params = []
    if search_value:
        if search_type == 'name':
            query += ' WHERE b.BName LIKE ?'
            params.append(f'%{search_value}%')
        elif search_type == 'author':
            query += ' WHERE b.BAuthor LIKE ?'
            params.append(f'%{search_value}%')
        elif search_type == 'type':
            query += ' WHERE bt.BTName LIKE ?'
            params.append(f'%{search_value}%')
    
    query += ' ORDER BY b.BNo'
    
    # 执行查询
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    books = cursor.fetchall()
    conn.close()
    
    # 渲染模板
    return render_template('admin_books.html', books=books)

# 办理借书
@app.route('/api/borrow', methods=['POST'])
@login_required
def borrow_book():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    try:
        data = request.json
        card_number = data.get('card_number')
        book_number = data.get('book_number')
        borrow_days = int(data.get('borrow_days', 30))
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 1. 检查借阅卡是否存在且有效
        cursor.execute('SELECT RNo, CW FROM bookcredit WHERE CNo = ?', (card_number,))
        card_info = cursor.fetchone()
        
        if not card_info:
            conn.close()
            return jsonify({'success': False, 'message': '借阅卡不存在'})
        
        if card_info[1] == '1':  # CW=1表示挂失
            conn.close()
            return jsonify({'success': False, 'message': '借阅卡已挂失'})
        
        # 2. 检查图书是否存在且有库存
        cursor.execute('SELECT Biomass FROM book WHERE BNo = ?', (book_number,))
        book_info = cursor.fetchone()
        
        if not book_info:
            conn.close()
            return jsonify({'success': False, 'message': '图书不存在'})
        
        if book_info[0] <= 0:
            conn.close()
            return jsonify({'success': False, 'message': '图书库存不足'})
        
        # 3. 检查读者是否已借满
        cursor.execute('SELECT CNum FROM bookcredit WHERE CNo = ?', (card_number,))
        max_borrow = cursor.fetchone()[0] or 5
        
        cursor.execute('SELECT COUNT(*) FROM borrow WHERE CNo = ? AND (BBBTime IS NULL OR BBBTime = "")', (card_number,))
        current_borrow = cursor.fetchone()[0] or 0
        
        if current_borrow >= max_borrow:
            conn.close()
            return jsonify({'success': False, 'message': f'借阅卡已借满（最多{max_borrow}本）'})
        
        # 4. 检查是否已借过该书且未还
        cursor.execute('SELECT COUNT(*) FROM borrow WHERE CNo = ? AND BNo = ? AND (BBBTime IS NULL OR BBBTime = "")', (card_number, book_number))
        already_borrowed = cursor.fetchone()[0] or 0
        
        if already_borrowed > 0:
            conn.close()
            return jsonify({'success': False, 'message': '您已借阅此书且未归还'})
        
        # 5. 办理借书
        borrow_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO borrow (CNo, BNo, BBTime, BBBTime, BBFine, BBW)
            VALUES (?, ?, ?, NULL, 0.0, '0')
        ''', (card_number, book_number, borrow_time))
        
        # 6. 减少图书现存量
        cursor.execute('UPDATE book SET Biomass = Biomass - 1 WHERE BNo = ?', (book_number,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'借书成功！借阅卡号：{card_number}，图书编号：{book_number}',
            'borrow_time': borrow_time
        })
        
    except Exception as e:
        print(f"借书出错: {e}")
        return jsonify({'success': False, 'message': f'借书失败：{str(e)}'})

# 办理还书
@app.route('/api/return', methods=['POST'])
@login_required
def return_book():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    try:
        data = request.json
        card_number = data.get('card_number')
        book_number = data.get('book_number')
        return_status = data.get('return_status', 'normal')
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 1. 检查是否有对应的借书记录
        cursor.execute('''
            SELECT BBTime, BBFine FROM borrow 
            WHERE CNo = ? AND BNo = ? AND (BBBTime IS NULL OR BBBTime = "")
        ''', (card_number, book_number))
        
        borrow_record = cursor.fetchone()
        
        if not borrow_record:
            conn.close()
            return jsonify({'success': False, 'message': '没有找到对应的借书记录'})
        
        borrow_time = borrow_record[0]
        current_fine = borrow_record[1] or 0
        
        # 获取图书信息
        cursor.execute('SELECT BName, Price, Biomass, TotalNum FROM book WHERE BNo = ?', (book_number,))
        book_info = cursor.fetchone()
        book_name = book_info[0] if book_info else "未知图书"
        book_price = book_info[1] if book_info else 0
        book_biomass = book_info[2] if book_info else 0
        book_total = book_info[3] if book_info else 0
        
        # 获取读者信息
        cursor.execute('SELECT RName FROM reader WHERE CNo = ?', (card_number,))
        reader_result = cursor.fetchone()
        reader_name = reader_result[0] if reader_result else "未知读者"
        
        # 2. 计算是否逾期和罚款
        new_fine = current_fine
        fines_to_add = 0
        overdue_days = 0
        
        if return_status == 'normal':
            # 计算逾期天数
            if borrow_time:
                try:
                    borrow_date = datetime.strptime(borrow_time, '%Y-%m-%d %H:%M:%S')
                    current_date = datetime.now()
                    days_borrowed = (current_date - borrow_date).days
                    
                    if days_borrowed > 30:
                        overdue_days = days_borrowed - 30
                        overdue_fine = overdue_days * 1.0
                        fines_to_add = overdue_fine
                        new_fine = current_fine + overdue_fine
                        
                        # 更新读者罚款
                        cursor.execute('UPDATE reader SET RFine = RFine + ? WHERE CNo = ?', (overdue_fine, card_number))
                        # 更新书卡罚款
                        cursor.execute('UPDATE bookcredit SET CFine = CFine + ? WHERE CNo = ?', (overdue_fine, card_number))
                except Exception as e:
                    print(f"[WARNING] 计算逾期天数出错: {e}")
        
        elif return_status == 'damaged':
            # 损坏罚款：图书价格的一半
            damage_fine = book_price * 0.5
            fines_to_add = damage_fine
            new_fine = current_fine + damage_fine
            
            # 更新罚款记录
            cursor.execute('UPDATE reader SET RFine = RFine + ? WHERE CNo = ?', (damage_fine, card_number))
            cursor.execute('UPDATE bookcredit SET CFine = CFine + ? WHERE CNo = ?', (damage_fine, card_number))
            
        elif return_status == 'lost':
            # 丢失罚款：图书价格的2倍
            lost_fine = book_price * 2.0
            fines_to_add = lost_fine
            new_fine = current_fine + lost_fine
            
            # 更新罚款记录
            cursor.execute('UPDATE reader SET RFine = RFine + ? WHERE CNo = ?', (lost_fine, card_number))
            cursor.execute('UPDATE bookcredit SET CFine = CFine + ? WHERE CNo = ?', (lost_fine, card_number))
        
        # 3. 如果有罚款，添加到 fine 表和 fine_detail 表
        if fines_to_add > 0:
            try:
                # 确保 fine 表和 fine_detail 表存在
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fine'")
                if not cursor.fetchone():
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS fine (
                            FNo CHAR(18) PRIMARY KEY,
                            CNo CHAR(12),
                            FTime DATETIME,
                            FFine NUMERIC(8,2)
                        )
                    ''')
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fine_detail'")
                if not cursor.fetchone():
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS fine_detail (
                            FDNo VARCHAR(20) PRIMARY KEY,
                            FNo CHAR(18),
                            BNo VARCHAR(20),
                            Reason VARCHAR(100),
                            FineAmount NUMERIC(8,2),
                            FOREIGN KEY (FNo) REFERENCES fine(FNo),
                            FOREIGN KEY (BNo) REFERENCES book(BNo)
                        )
                    ''')
                
                # 生成罚款单号
                cursor.execute('SELECT MAX(CAST(SUBSTR(FNo, 2) AS INTEGER)) FROM fine WHERE FNo LIKE "F%"')
                max_fno_result = cursor.fetchone()
                if max_fno_result and max_fno_result[0]:
                    max_fno = max_fno_result[0]
                    fine_no = f"F{max_fno + 1:03d}"
                else:
                    fine_no = "F001"
                
                # 插入罚款主记录
                cursor.execute('''
                    INSERT INTO fine (FNo, CNo, FTime, FFine)
                    VALUES (?, ?, datetime('now'), ?)
                ''', (fine_no, card_number, fines_to_add))
                
                # 生成罚款详细记录编号
                cursor.execute('SELECT MAX(CAST(SUBSTR(FDNo, 3) AS INTEGER)) FROM fine_detail WHERE FDNo LIKE "FD%"')
                max_fdno_result = cursor.fetchone()
                if max_fdno_result and max_fdno_result[0]:
                    max_fdno = max_fdno_result[0]
                    fine_detail_no = f"FD{max_fdno + 1:03d}"
                else:
                    fine_detail_no = "FD001"
                
                # 创建罚款原因描述
                reason_desc = ""
                if return_status == 'normal' and overdue_days > 0:
                    reason_desc = f"图书《{book_name}》逾期{overdue_days}天"
                elif return_status == 'damaged':
                    reason_desc = f"图书《{book_name}》损坏"
                elif return_status == 'lost':
                    reason_desc = f"图书《{book_name}》丢失"
                
                # 插入罚款详细记录
                cursor.execute('''
                    INSERT INTO fine_detail (FDNo, FNo, BNo, Reason, FineAmount)
                    VALUES (?, ?, ?, ?, ?)
                ''', (fine_detail_no, fine_no, book_number, reason_desc, fines_to_add))
                
                print(f"[DEBUG] 添加罚款记录：罚款单号={fine_no}, 金额={fines_to_add}, 原因={reason_desc}")
                
            except Exception as e:
                print(f"[ERROR] 添加罚款记录失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 4. 如果是丢失或损坏，创建报损记录
        damage_no = None
        if return_status in ['damaged', 'lost']:
            try:
                # 生成报损单号
                cursor.execute('SELECT MAX(CAST(SUBSTR(BANO, 3) AS INTEGER)) FROM breakage WHERE BANO LIKE "BD%"')
                result = cursor.fetchone()
                if result and result[0]:
                    max_ban = result[0]
                    damage_no = f"BD{max_ban + 1:03d}"
                else:
                    damage_no = "BD001"
                
                # 生成报损明细单号
                cursor.execute('SELECT MAX(CAST(SUBSTR(BADNo, 3) AS INTEGER)) FROM breakageDetail WHERE BADNo LIKE "BAD%"')
                result = cursor.fetchone()
                if result and result[0]:
                    max_bad = result[0]
                    bad_no = f"BAD{max_bad + 1:03d}"
                else:
                    bad_no = "BAD001"
                
                # 获取当前管理员
                cursor.execute('SELECT MNo, MName FROM manager LIMIT 1')
                manager_result = cursor.fetchone()
                manager_no = manager_result[0] if manager_result else 'M001'
                manager_name = manager_result[1] if manager_result else '管理员'
                
                # 报损原因描述
                if return_status == 'lost':
                    if overdue_days > 0:
                        damage_reason = f"读者[{reader_name}]还书时标记为丢失（逾期{overdue_days}天）"
                    else:
                        damage_reason = f"读者[{reader_name}]还书时标记为丢失"
                else:  # damaged
                    if overdue_days > 0:
                        damage_reason = f"读者[{reader_name}]还书时标记为损坏（逾期{overdue_days}天）"
                    else:
                        damage_reason = f"读者[{reader_name}]还书时标记为损坏"
                
                # 当前时间
                damage_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 创建报损主记录
                cursor.execute('''
                    INSERT INTO breakage (BANO, BADNo, BATime, BASum, MNO)
                    VALUES (?, ?, ?, ?, ?)
                ''', (damage_no, bad_no, damage_date, 1, manager_no))
                
                # 创建报损明细记录
                cursor.execute('''
                    INSERT INTO breakageDetail (BADNo, BNo, Reasons, BADNum)
                    VALUES (?, ?, ?, ?)
                ''', (bad_no, book_number, damage_reason, 1))
                
                print(f"[INFO] 创建还书报损记录：报损单号={damage_no}, 图书={book_name}({book_number}), 原因={damage_reason}")
                
            except Exception as e:
                print(f"[ERROR] 创建报损记录失败: {e}")
                import traceback
                traceback.print_exc()
                # 继续执行，不中断主要流程
        
        # 5. 办理还书
        return_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            UPDATE borrow 
            SET BBBTime = ?, BBFine = ?
            WHERE CNo = ? AND BNo = ? AND (BBBTime IS NULL OR BBBTime = "")
        ''', (return_time, new_fine, card_number, book_number))
        
        # 6. 更新图书库存
        stock_change_message = ""
        if return_status == 'normal':
            # 正常还书：增加现存量
            cursor.execute('UPDATE book SET Biomass = Biomass + 1 WHERE BNo = ?', (book_number,))
            stock_change_message = "图书现存量+1"
        elif return_status == 'lost':
            # 图书丢失：减少总数量和现存量
            cursor.execute('UPDATE book SET TotalNum = TotalNum - 1, Biomass = Biomass - 1 WHERE BNo = ?', (book_number,))
            stock_change_message = "图书总数量和现存量各-1"
            print(f"[INFO] 图书《{book_name}》标记为丢失，总数量减少1，现存量减少1")
        elif return_status == 'damaged':
            # 图书损坏：减少现存量（因为损坏的书不能继续借阅）
            # 总数量不变（因为书还在，只是损坏了）
            cursor.execute('UPDATE book SET Biomass = Biomass - 1 WHERE BNo = ?', (book_number,))
            stock_change_message = "图书现存量-1（损坏）"
            print(f"[INFO] 图书《{book_name}》标记为损坏，现存量减少1")
        
        conn.commit()
        
        # 7. 再次同步罚款数据
        if fines_to_add > 0:
            try:
                # 重新计算罚款总额
                cursor.execute('SELECT SUM(FFine) FROM fine WHERE CNo = ? AND FFine > 0', (card_number,))
                total_fine_result = cursor.fetchone()
                total_fine = float(total_fine_result[0]) if total_fine_result and total_fine_result[0] else 0.0
                
                # 更新 reader 表和 bookcredit 表
                cursor.execute('UPDATE reader SET RFine = ? WHERE CNo = ?', (total_fine, card_number))
                cursor.execute('UPDATE bookcredit SET CFine = ? WHERE CNo = ?', (total_fine, card_number))
                conn.commit()
                print(f"[DEBUG] 同步罚款数据：读者卡号={card_number}, 总罚款={total_fine}")
            except Exception as e:
                print(f"[ERROR] 同步罚款数据失败: {e}")
        
        # 获取更新后的图书信息用于返回
        cursor.execute('SELECT Biomass, TotalNum FROM book WHERE BNo = ?', (book_number,))
        updated_book_info = cursor.fetchone()
        updated_biomass = updated_book_info[0] if updated_book_info else book_biomass
        updated_total = updated_book_info[1] if updated_book_info else book_total
        
        conn.close()
        
        # 8. 返回结果
        fine_message = ""
        if fines_to_add > 0:
            fine_message = f" 产生罚款：¥{fines_to_add:.2f}"
            if 'fine_no' in locals():
                fine_message += f"（罚款单号：{fine_no}）"
        
        # 如果是损坏或丢失，添加报损记录提示
        damage_message = ""
        if return_status in ['damaged', 'lost'] and damage_no:
            damage_message = f" 已创建报损记录（报损单号：{damage_no}）"
        
        return jsonify({
            'success': True, 
            'message': f'还书成功！{stock_change_message}{fine_message}{damage_message}',
            'return_time': return_time,
            'fine': new_fine,
            'damage_record_created': return_status in ['damaged', 'lost'],
            'damage_no': damage_no,
            'book_info': {
                'book_number': book_number,
                'book_name': book_name,
                'current_biomass': updated_biomass,
                'current_total': updated_total,
                'status': return_status
            },
            'reader_info': {
                'card_number': card_number,
                'reader_name': reader_name
            }
        })
        
    except Exception as e:
        print(f"还书出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'还书失败：{str(e)}'})


# 查询罚款详细信息API
@app.route('/api/fine/<fine_number>/details')
@login_required
def get_fine_details(fine_number):
    if session.get('user_type') not in ['admin', 'reader']:
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 查询罚款主信息
        cursor.execute('''
            SELECT f.FNo, f.CNo, f.FTime, f.FFine, r.RName, r.RNo
            FROM fine f
            JOIN reader r ON f.CNo = r.CNo
            WHERE f.FNo = ?
        ''', (fine_number,))
        
        fine_info = cursor.fetchone()
        
        if not fine_info:
            conn.close()
            return jsonify({'success': False, 'message': '罚款记录不存在'}), 404
        
        # 查询罚款详细信息
        cursor.execute('''
            SELECT fd.FDNo, fd.BNo, b.BName, fd.Reason, fd.FineAmount
            FROM fine_detail fd
            LEFT JOIN book b ON fd.BNo = b.BNo
            WHERE fd.FNo = ?
            ORDER BY fd.FDNo
        ''', (fine_number,))
        
        fine_details = cursor.fetchall()
        
        conn.close()
        
        # 格式化返回数据
        details_list = []
        total_amount = 0
        
        for detail in fine_details:
            details_list.append({
                'detail_no': detail[0],
                'book_number': detail[1],
                'book_name': detail[2] or '未知图书',
                'reason': detail[3],
                'amount': float(detail[4] or 0)
            })
            total_amount += float(detail[4] or 0)
        
        fine_data = {
            'fine_number': fine_info[0],
            'card_number': fine_info[1],
            'fine_date': fine_info[2],
            'total_fine': float(fine_info[3] or 0),
            'reader_name': fine_info[4],
            'reader_number': fine_info[5],
            'calculated_total': total_amount,
            'details': details_list
        }
        
        return jsonify({'success': True, 'fine': fine_data})
        
    except Exception as e:
        print(f"查询罚款详细信息出错: {e}")
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500

# 借阅查询
@app.route('/api/borrows', methods=['GET'])
@login_required
def query_borrows():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    card_number = request.args.get('card_number', '')
    book_number = request.args.get('book_number', '')
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    query = '''
        SELECT b.CNo, b.BNo, bk.BName, r.RName, b.BBTime, 
               b.BBBTime, b.BBFine, b.BBW,
               DATE(b.BBTime, '+30 days') as DueDate
        FROM borrow b
        JOIN book bk ON b.BNo = bk.BNo
        JOIN bookcredit bc ON b.CNo = bc.CNo
        JOIN reader r ON bc.RNo = r.RNo
        WHERE 1=1
    '''
    params = []
    
    if card_number:
        query += ' AND b.CNo LIKE ?'
        params.append(f'%{card_number}%')
    
    if book_number:
        query += ' AND b.BNo LIKE ?'
        params.append(f'%{book_number}%')
    
    query += ' ORDER BY b.BBTime DESC'
    
    cursor.execute(query, params)
    borrows = cursor.fetchall()
    
    results = []
    for borrow in borrows:
        # 判断是否逾期
        is_overdue = False
        status = "已还"
        if borrow[5] is None or borrow[5] == '':  # BBBTime为空表示未还
            status = "在借"
            if borrow[4]:  # 如果有借书时间
                try:
                    borrow_date = datetime.strptime(borrow[4], '%Y-%m-%d %H:%M:%S')
                    days_borrowed = (datetime.now() - borrow_date).days
                    is_overdue = days_borrowed > 30
                except:
                    pass
        
        results.append({
            'card_number': borrow[0],
            'book_number': borrow[1],
            'book_name': borrow[2],
            'reader_name': borrow[3],
            'borrow_date': borrow[4],
            'return_date': borrow[5],
            'fine': borrow[6],
            'status': status,
            'is_overdue': is_overdue,
            'due_date': borrow[7]
        })
    
    conn.close()
    
    return jsonify({'success': True, 'borrows': results})

# 续借功能
@app.route('/api/renew', methods=['POST'])
@login_required
def renew_book():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    try:
        data = request.json
        card_number = data.get('card_number')
        book_number = data.get('book_number')
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 检查是否已续借过
        cursor.execute('SELECT BBW FROM borrow WHERE CNo = ? AND BNo = ? AND (BBBTime IS NULL OR BBBTime = "")', (card_number, book_number))
        borrow_info = cursor.fetchone()
        
        if not borrow_info:
            conn.close()
            return jsonify({'success': False, 'message': '没有找到对应的借书记录'})
        
        if borrow_info[0] == '1':  # BBW=1表示已续借
            conn.close()
            return jsonify({'success': False, 'message': '该书已续借过，不能再次续借'})
        
        # 办理续借
        cursor.execute('UPDATE borrow SET BBW = "1" WHERE CNo = ? AND BNo = ? AND (BBBTime IS NULL OR BBBTime = "")', (card_number, book_number))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '续借成功！借期延长30天'})
        
    except Exception as e:
        print(f"续借出错: {e}")
        return jsonify({'success': False, 'message': f'续借失败：{str(e)}'})
    

# 图书API - 获取单本图书
@app.route('/api/books/<book_number>')
@login_required
def get_book(book_number):
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.BNo, b.BName, b.BAuthor, bt.BTName, p.PName, b.Price, b.TotalNum, b.Biomass
        FROM book b
        LEFT JOIN booktype bt ON b.BTNo = bt.BTNo
        LEFT JOIN publisher p ON b.PNo = p.PNo
        WHERE b.BNo = ?
    ''', (book_number,))
    
    book = cursor.fetchone()
    conn.close()
    
    if book:
        # 转换为字典
        book_dict = {
            'BNo': book[0],
            'BName': book[1],
            'BAuthor': book[2],
            'BTName': book[3],
            'PName': book[4],
            'Price': book[5],
            'TotalNum': book[6],
            'Biomass': book[7]
        }
        return jsonify({'success': True, 'book': book_dict})
    else:
        return jsonify({'success': False, 'message': '图书不存在'})

# 图书API - 删除图书
@app.route('/api/books/<book_number>', methods=['DELETE'])
@login_required
def delete_book(book_number):
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 检查图书是否被借出
        cursor.execute('SELECT COUNT(*) FROM borrow WHERE BNo = ? AND BBBTime IS NULL', (book_number,))
        borrowed_count = cursor.fetchone()[0]
        
        if borrowed_count > 0:
            conn.close()
            return jsonify({'success': False, 'message': '该书已被借出，无法删除'})
        
        # 删除图书
        cursor.execute('DELETE FROM book WHERE BNo = ?', (book_number,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})

# 图书API - 更新图书
@app.route('/api/books/<book_number>', methods=['PUT'])
@login_required
def update_book(book_number):
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    try:
        data = request.json
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 更新图书信息
        cursor.execute('''
            UPDATE book SET 
            BName = ?, BAuthor = ?, Price = ?, TotalNum = ?, Biomass = ?
            WHERE BNo = ?
        ''', (
            data.get('BName'),
            data.get('BAuthor'),
            data.get('Price'),
            data.get('TotalNum'),
            data.get('Biomass'),
            book_number
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})

# 编辑图书页面路由
@app.route('/admin/edit_book/<book_number>')
@login_required
def edit_book(book_number):
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    return render_template('edit_book.html')

# 编辑读者页面路由
@app.route('/admin/edit_reader/<reader_number>')
@login_required
def edit_reader_page(reader_number):
    print(f"[DEBUG] 访问编辑读者页面: {reader_number}")
    
    if session.get('user_type') != 'admin':
        print("[DEBUG] 用户不是管理员，重定向到登录页")
        return redirect(url_for('login'))
    
    # 验证读者编号格式
    if not reader_number or not reader_number.startswith('R') or len(reader_number) < 3:
        print(f"[DEBUG] 读者编号格式无效: {reader_number}")
        return render_template('error.html', error='读者编号格式无效')
    
    return render_template('edit_reader.html')

# 添加读者页面路由
@app.route('/admin/add_reader')
@login_required
def add_reader_page():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    return render_template('add_reader.html')

# 添加图书页面路由
@app.route('/admin/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        bno = request.form['bno']
        bname = request.form['bname']
        bauthor = request.form['bauthor']
        btno = request.form['btno']
        pno = request.form['pno']
        price = request.form['price']
        total_num = request.form['total_num']
        publish_time = request.form.get('publish_time', datetime.now().strftime('%Y-%m-%d'))

        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO book (BNo, BName, BAuthor, BTNo, PNo, Price, PTime, InputTime, TotalNum, Biomass)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, ?)
            ''', (bno, bname, bauthor, btno, pno, price, publish_time, total_num, total_num))
            conn.commit()
            
            # 添加成功提示
            flash('图书添加成功！', 'success')
            return redirect(url_for('admin_books'))
        except sqlite3.IntegrityError as e:
            conn.rollback()
            flash(f'添加失败：图书编号已存在或数据格式错误', 'error')
        except Exception as e:
            conn.rollback()
            flash(f'添加失败：{str(e)}', 'error')
        finally:
            conn.close()

    # GET 请求：显示表单
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT BTNo, BTName FROM booktype')
    booktypes = cursor.fetchall()
    cursor.execute('SELECT PNo, PName FROM publisher')
    publishers = cursor.fetchall()
    conn.close()

    return render_template('add_book.html', booktypes=booktypes, publishers=publishers)

# 读者搜索功能
@app.route('/admin/search_readers')
@login_required
def search_readers():
    if session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    search_type = request.args.get('search_type', 'name')
    search_value = request.args.get('search_value', '')
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # 构建查询
    query = '''
        SELECT r.RNo, r.CNo, r.RName, r.RSex, r.RIDNum, r.RFine, 
               bc.CNum, bc.CW, bc.CDate, bc.Crenew
        FROM reader r
        LEFT JOIN bookcredit bc ON r.CNo = bc.CNo
        WHERE 1=1
    '''
    
    params = []
    
    if search_value:
        if search_type == 'name':
            query += ' AND r.RName LIKE ?'
            params.append(f'%{search_value}%')
        elif search_type == 'card':
            query += ' AND r.CNo LIKE ?'
            params.append(f'%{search_value}%')
        elif search_type == 'id':
            query += ' AND r.RIDNum LIKE ?'
            params.append(f'%{search_value}%')
    
    cursor.execute(query, params)
    readers_data = cursor.fetchall()
    
    # 处理数据
    readers = []
    for reader in readers_data:
        # 计算已借册数
        cursor.execute('SELECT COUNT(*) FROM borrow WHERE CNo = ? AND (BBBTime IS NULL OR BBBTime = "")', (reader[1],))
        borrowed_count = cursor.fetchone()[0] or 0
        
        readers.append({
            'reader_number': reader[0],
            'card_number': reader[1],
            'reader_name': reader[2],
            'sex': reader[3],
            'id_number': reader[4],
            'unpaid_fine': reader[5],
            'borrowable_books': reader[6] if reader[6] else 5,
            'borrowed_books': borrowed_count,
            'is_lost': reader[7] == '1' if reader[7] else False,
            'card_date': reader[8],
            'renew_date': reader[9],
        })
    
    conn.close()
    
    return render_template('search_readers.html', 
                         readers=readers, 
                         search_type=search_type,
                         search_value=search_value)

# 读者API - 获取单条读者信息
@app.route('/api/readers/<reader_number>', methods=['GET'])
@login_required
def get_reader(reader_number):
    print(f"[DEBUG] 收到API请求: GET /api/readers/{reader_number}")
    print(f"[DEBUG] 用户类型: {session.get('user_type')}")
    
    if session.get('user_type') != 'admin':
        print("[DEBUG] 权限不足，返回403")
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 查询读者基本信息
        cursor.execute('''
            SELECT r.RNo, r.CNo, r.RName, r.RSex, r.RIDNum, r.RFine, 
                   bc.CNum, bc.CW, bc.Crenew, bc.CDate
            FROM reader r
            LEFT JOIN bookcredit bc ON r.CNo = bc.CNo
            WHERE r.RNo = ?
        ''', (reader_number,))
        
        reader = cursor.fetchone()
        print(f"[DEBUG] 数据库查询结果: {reader}")
        
        if reader:
            # 计算已借册数
            cursor.execute('SELECT COUNT(*) FROM borrow WHERE CNo = ? AND (BBBTime IS NULL OR BBBTime = "")', (reader[1],))
            borrowed_count = cursor.fetchone()[0] or 0
            
            # 计算借期天数
            borrow_days = 30  # 默认值
            if reader[8] and reader[9]:  # Crenew 和 CDate
                try:
                    # 计算天数差
                    cursor.execute('SELECT julianday(?) - julianday(?)', (reader[8], reader[9]))
                    days_result = cursor.fetchone()
                    if days_result and days_result[0]:
                        borrow_days = int(days_result[0])
                except Exception as e:
                    print(f"[WARNING] 计算借期天数出错: {e}")
                    borrow_days = 30
            
            # 获取借阅历史
            cursor.execute('''
                SELECT b.BNo, bk.BName, b.BBTime, b.BBBTime, b.BBFine,
                       CASE 
                           WHEN b.BBBTime IS NULL OR b.BBBTime = '' THEN '在借'
                           ELSE '已还'
                       END as status
                FROM borrow b
                JOIN book bk ON b.BNo = bk.BNo
                WHERE b.CNo = ?
                ORDER BY b.BBTime DESC
                LIMIT 20
            ''', (reader[1],))
            
            borrow_history = cursor.fetchall()
            conn.close()
            
            reader_info = {
                'reader_number': reader[0],
                'card_number': reader[1],
                'reader_name': reader[2],
                'sex': reader[3],
                'id_number': reader[4],
                'unpaid_fine': float(reader[5] or 0),
                'borrowable_books': reader[6] if reader[6] else 5,
                'borrowed_books': borrowed_count,
                'is_lost': reader[7] == '1' if reader[7] else False,
                'borrow_days': borrow_days
            }
            
            # 格式化借阅历史
            history_list = []
            for borrow in borrow_history:
                history_list.append({
                    'book_number': borrow[0],
                    'book_name': borrow[1],
                    'borrow_date': borrow[2],
                    'return_date': borrow[3],
                    'fine': float(borrow[4] or 0) if borrow[4] else 0,
                    'status': borrow[5]
                })
            
            print(f"[DEBUG] 成功返回读者信息: {reader_info}")
            response_data = jsonify({
                'success': True, 
                'reader': reader_info,
                'borrow_history': history_list
            })
            
            # 确保设置正确的Content-Type
            response_data.headers['Content-Type'] = 'application/json'
            return response_data
            
        else:
            conn.close()
            print(f"[DEBUG] 读者不存在: {reader_number}")
            response_data = jsonify({'success': False, 'message': f'读者 {reader_number} 不存在'})
            response_data.headers['Content-Type'] = 'application/json'
            return response_data, 404
            
    except Exception as e:
        print(f"[ERROR] 获取读者信息出错: {e}")
        import traceback
        traceback.print_exc()
        response_data = jsonify({'success': False, 'message': f'服务器错误: {str(e)}'})
        response_data.headers['Content-Type'] = 'application/json'
        return response_data, 500


# 切换借阅卡挂失状态API
@app.route('/api/cards/<card_number>/toggle-lost', methods=['POST'])
@login_required
def toggle_lost_card(card_number):
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 获取当前状态
        cursor.execute('SELECT CW FROM bookcredit WHERE CNo = ?', (card_number,))
        card_status = cursor.fetchone()
        
        if not card_status:
            conn.close()
            return jsonify({'success': False, 'message': '借阅卡不存在'})
        
        current_status = card_status[0]
        new_status = '0' if current_status == '1' else '1'  # 切换状态
        status_text = '挂失' if new_status == '1' else '解挂'
        
        # 更新状态
        cursor.execute('UPDATE bookcredit SET CW = ? WHERE CNo = ?', (new_status, card_number))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f'借阅卡{status_text}成功'})
        
    except Exception as e:
        print(f"切换借阅卡状态出错: {e}")
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'})
    
# 读者API - 更新读者信息
@app.route('/api/readers/<reader_number>', methods=['PUT'])
@login_required
def update_reader(reader_number):
    print(f"[DEBUG] 收到API请求: PUT /api/readers/{reader_number}")
    
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        data = request.get_json()
        print(f"[DEBUG] 接收到的数据: {data}")
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 首先检查读者是否存在
        cursor.execute('SELECT CNo FROM reader WHERE RNo = ?', (reader_number,))
        reader = cursor.fetchone()
        
        if not reader:
            conn.close()
            return jsonify({'success': False, 'message': '读者不存在'}), 404
        
        card_number = reader[0]
        
        # 更新读者基本信息
        update_fields = []
        update_values = []
        
        if 'reader_name' in data:
            update_fields.append('RName = ?')
            update_values.append(data['reader_name'].strip())
        
        if 'sex' in data:
            update_fields.append('RSex = ?')
            update_values.append(data['sex'].strip())
        
        if 'id_number' in data:
            update_fields.append('RIDNum = ?')
            update_values.append(data['id_number'].strip())
        
        if update_fields:
            update_query = f'UPDATE reader SET {", ".join(update_fields)} WHERE RNo = ?'
            update_values.append(reader_number)
            cursor.execute(update_query, update_values)
            print(f"[DEBUG] 更新reader表: {update_query}, 参数: {update_values}")
        
        # 更新借阅卡信息
        card_update_fields = []
        card_update_values = []
        
        if 'borrowable_books' in data:
            card_update_fields.append('CNum = ?')
            card_update_values.append(data['borrowable_books'])
        
        if 'borrow_days' in data:
            # 更新续借日期
            borrow_days = data['borrow_days']
            cursor.execute('UPDATE bookcredit SET Crenew = datetime(CDate, ? || " days") WHERE CNo = ?', 
                         (borrow_days, card_number))
            print(f"[DEBUG] 更新借期天数: {borrow_days}天，卡号: {card_number}")
        
        if card_update_fields:
            card_update_query = f'UPDATE bookcredit SET {", ".join(card_update_fields)} WHERE CNo = ?'
            card_update_values.append(card_number)
            cursor.execute(card_update_query, card_update_values)
            print(f"[DEBUG] 更新bookcredit表: {card_update_query}, 参数: {card_update_values}")
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '读者信息更新成功'})
        
    except Exception as e:
        print(f"[ERROR] 更新读者信息出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

# 读者API - 添加读者
@app.route('/api/readers', methods=['POST'])
@login_required
def add_reader():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    try:
        data = request.json
        
        # 提取数据并设置默认值
        reader_name = data.get('reader_name', '').strip()
        sex = data.get('sex', '').strip()
        id_number = data.get('id_number', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        borrowable_books = int(data.get('borrowable_books', 5))
        borrow_days = int(data.get('borrow_days', 30))
        
        # 验证必填字段
        if not all([reader_name, sex, id_number, username, password]):
            return jsonify({'success': False, 'message': '请填写所有必填字段'})
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': '密码长度至少6位'})
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 检查用户名是否已存在
        cursor.execute('SELECT COUNT(*) FROM reader WHERE username = ?', (username,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return jsonify({'success': False, 'message': '用户名已存在'})
        
        # 检查身份证号是否已存在
        cursor.execute('SELECT COUNT(*) FROM reader WHERE RIDNum = ?', (id_number,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return jsonify({'success': False, 'message': '身份证号已存在'})
        
        # 生成读者编号
        cursor.execute('SELECT MAX(CAST(SUBSTR(RNo, 2) AS INTEGER)) FROM reader WHERE RNo LIKE "R%"')
        result = cursor.fetchone()
        if result and result[0]:
            max_rno = result[0]
            new_rno = f"R{max_rno + 1:03d}"
        else:
            new_rno = "R001"
        
        # 生成借阅卡号
        cursor.execute('SELECT MAX(CAST(SUBSTR(CNo, 2) AS INTEGER)) FROM bookcredit WHERE CNo LIKE "C%"')
        result = cursor.fetchone()
        if result and result[0]:
            max_cno = result[0]
            new_cno = f"C{max_cno + 1:03d}"
        else:
            new_cno = "C001"
        
        # 插入读者数据
        cursor.execute('''
            INSERT INTO reader (RNo, CNo, RName, RSex, RIDNum, RFine, username, password)
            VALUES (?, ?, ?, ?, ?, 0.0, ?, ?)
        ''', (new_rno, new_cno, reader_name, sex, id_number, username, password))
        
        # 创建借阅卡记录 - 修复这里的SQL语句
        cursor.execute(f'''
            INSERT INTO bookcredit (CNo, RNo, CFine, CNum, CW, CDate, Crenew)
            VALUES (?, ?, 0.0, ?, '0', datetime('now'), datetime('now', '+{borrow_days} days'))
        ''', (new_cno, new_rno, borrowable_books))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': '读者添加成功',
            'reader_number': new_rno,
            'card_number': new_cno,
            'reader_name': reader_name
        })
        
    except sqlite3.IntegrityError as e:
        return jsonify({'success': False, 'message': '数据库完整性错误，可能数据已存在'})
    except Exception as e:
        print(f"添加读者出错: {e}")
        return jsonify({'success': False, 'message': f'添加读者失败：{str(e)}'})

# 我的借阅页面
@app.route('/reader/borrows')
@login_required
def reader_borrows():
    if session.get('user_type') != 'reader':
        return redirect(url_for('login'))
    return render_template('reader_borrows.html')

# 我的借阅API
@app.route('/api/reader/borrows', methods=['GET'])
@login_required
def reader_borrows_api():
    if session.get('user_type') != 'reader':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        reader_id = session.get('user_id')
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 获取读者的借阅卡号
        cursor.execute('SELECT CNo FROM reader WHERE RNo = ?', (reader_id,))
        reader_result = cursor.fetchone()
        
        if not reader_result:
            conn.close()
            return jsonify({'success': False, 'message': '读者信息不存在'}), 404
        
        card_number = reader_result[0]
        
        # 查询当前借阅记录
        cursor.execute('''
            SELECT b.CNo, b.BNo, bk.BName, bk.BAuthor, b.BBTime, 
                   b.BBBTime, b.BBFine, b.BBW,
                   CASE 
                       WHEN b.BBBTime IS NULL OR b.BBBTime = '' THEN '在借'
                       ELSE '已还'
                   END as status
            FROM borrow b
            JOIN book bk ON b.BNo = bk.BNo
            WHERE b.CNo = ?
            ORDER BY b.BBTime DESC
        ''', (card_number,))
        
        borrows = cursor.fetchall()
        
        # 计算统计信息
        active_borrows = 0
        overdue_count = 0
        total_fine = 0.0
        
        borrows_list = []
        for borrow in borrows:
            # 解析数据
            book_number = borrow[1]
            book_name = borrow[2]
            author = borrow[3]
            borrow_date = borrow[4]
            return_date = borrow[5]
            fine = float(borrow[6] or 0)
            is_renewed = borrow[7] == '1'
            status = borrow[8]
            
            # 计算是否逾期
            is_overdue = False
            days_overdue = 0
            if status == '在借' and borrow_date:
                try:
                    # 计算借书天数
                    cursor.execute('SELECT julianday("now") - julianday(?)', (borrow_date,))
                    days_result = cursor.fetchone()
                    if days_result and days_result[0]:
                        days_borrowed = days_result[0]
                        if days_borrowed > 30:
                            is_overdue = True
                            days_overdue = int(days_borrowed - 30)
                except:
                    pass
            
            # 计算应还日期
            due_date = None
            if borrow_date:
                cursor.execute('SELECT date(?, "+30 days")', (borrow_date,))
                due_result = cursor.fetchone()
                due_date = due_result[0] if due_result else None
            
            # 更新统计
            if status == '在借':
                active_borrows += 1
                if is_overdue:
                    overdue_count += 1
            total_fine += fine
            
            borrows_list.append({
                'book_number': book_number,
                'book_name': book_name,
                'author': author or '未知',
                'borrow_date': borrow_date,
                'return_date': return_date,
                'fine': fine,
                'is_renewed': is_renewed,
                'status': status,
                'is_overdue': is_overdue,
                'days_overdue': days_overdue,
                'due_date': due_date
            })
        
        stats = {
            'total_borrows': len(borrows),
            'active_borrows': active_borrows,
            'renewed_books': len([b for b in borrows_list if b['is_renewed']]),
            'overdue_books': overdue_count,
            'total_fine': total_fine
        }
        
        conn.close()
        
        return jsonify({
            'success': True, 
            'borrows': borrows_list,
            'stats': stats
        })
        
    except Exception as e:
        print(f"获取读者借阅记录出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'获取记录失败: {str(e)}'}), 500

# 读者借阅API
@app.route('/api/reader/borrow/quick', methods=['POST'])
@login_required
def reader_borrow_quick_api():
    if session.get('user_type') != 'reader':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        data = request.json
        book_number = data.get('book_number')
        
        if not book_number:
            return jsonify({'success': False, 'message': '请选择要借阅的图书'}), 400
        
        reader_id = session.get('user_id')
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 1. 获取读者借阅卡状态
        cursor.execute('''
            SELECT r.CNo, bc.CW, r.RFine, bc.CNum
            FROM reader r
            LEFT JOIN bookcredit bc ON r.CNo = bc.CNo
            WHERE r.RNo = ?
        ''', (reader_id,))
        
        reader_info = cursor.fetchone()
        
        if not reader_info:
            conn.close()
            return jsonify({'success': False, 'message': '读者信息不存在'}), 404
        
        card_number = reader_info[0]
        card_status = reader_info[1]  # CW字段：0=正常，1=挂失
        reader_fine = float(reader_info[2] or 0)
        max_borrow = reader_info[3] or 5
        
        # 2. 检查借阅卡状态
        if card_status == '1':
            conn.close()
            return jsonify({'success': False, 'message': '借阅卡已挂失', 'code': 'CARD_LOST'})
        
        # 3. 检查未缴罚款
        if reader_fine > 0:
            conn.close()
            return jsonify({'success': False, 'message': '有未缴罚款，无法借阅', 'code': 'HAS_FINE', 'fine': reader_fine})
        
        # 4. 检查已借阅数量
        cursor.execute('SELECT COUNT(*) FROM borrow WHERE CNo = ? AND (BBBTime IS NULL OR BBBTime = "")', (card_number,))
        borrowed_count = cursor.fetchone()[0] or 0
        
        if borrowed_count >= max_borrow:
            conn.close()
            return jsonify({'success': False, 'message': f'已借满{max_borrow}本', 'code': 'MAX_BORROWED', 'current': borrowed_count, 'max': max_borrow})
        
        # 5. 检查图书库存
        cursor.execute('SELECT BNo, BName, Biomass FROM book WHERE BNo = ?', (book_number,))
        book_info = cursor.fetchone()
        
        if not book_info:
            conn.close()
            return jsonify({'success': False, 'message': '图书不存在', 'code': 'BOOK_NOT_FOUND'}), 404
        
        book_name = book_info[1]
        biomass = book_info[2] or 0
        
        if biomass <= 0:
            conn.close()
            return jsonify({'success': False, 'message': '图书库存不足', 'code': 'NO_STOCK'})
        
        # 6. 检查是否已借阅过该书
        cursor.execute('SELECT COUNT(*) FROM borrow WHERE CNo = ? AND BNo = ? AND (BBBTime IS NULL OR BBBTime = "")', (card_number, book_number))
        already_borrowed = cursor.fetchone()[0] or 0
        
        if already_borrowed > 0:
            conn.close()
            return jsonify({'success': False, 'message': '您已借阅此书', 'code': 'ALREADY_BORROWED'})
        
        # 7. 执行借阅操作
        borrow_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 插入借阅记录
        cursor.execute('''
            INSERT INTO borrow (CNo, BNo, BBTime, BBBTime, BBFine, BBW)
            VALUES (?, ?, ?, NULL, 0.0, '0')
        ''', (card_number, book_number, borrow_time))
        
        # 更新图书库存
        cursor.execute('UPDATE book SET Biomass = Biomass - 1 WHERE BNo = ?', (book_number,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '借阅成功',
            'code': 'BORROW_SUCCESS',
            'data': {
                'book_number': book_number,
                'book_name': book_name,
                'borrow_time': borrow_time,
                'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'borrowed_count': borrowed_count + 1,
                'max_borrow': max_borrow,
                'card_number': card_number,
                'reader_id': reader_id
            }
        })
        
    except sqlite3.IntegrityError as e:
        return jsonify({'success': False, 'message': '借阅失败，可能记录已存在', 'code': 'INTEGRITY_ERROR'}), 400
    except Exception as e:
        print(f"快速借阅出错: {e}")
        return jsonify({'success': False, 'message': '系统错误，请稍后重试', 'code': 'SYSTEM_ERROR'}), 500

# 读者借阅记录API - 获取最新借阅记录
@app.route('/api/reader/borrow/latest')
@login_required
def reader_borrow_latest_api():
    if session.get('user_type') != 'reader':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        reader_id = session.get('user_id')
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 获取读者卡号
        cursor.execute('SELECT CNo FROM reader WHERE RNo = ?', (reader_id,))
        reader_result = cursor.fetchone()
        
        if not reader_result:
            conn.close()
            return jsonify({'success': False, 'message': '读者信息不存在'}), 404
        
        card_number = reader_result[0]
        
        # 获取最新借阅记录
        cursor.execute('''
            SELECT b.BNo, bk.BName, b.BBTime, 
                   DATE(b.BBTime, '+30 days') as DueDate,
                   CASE 
                       WHEN b.BBBTime IS NULL OR b.BBBTime = '' THEN '在借'
                       ELSE '已还'
                   END as status
            FROM borrow b
            JOIN book bk ON b.BNo = bk.BNo
            WHERE b.CNo = ?
            ORDER BY b.BBTime DESC
            LIMIT 1
        ''', (card_number,))
        
        latest_borrow = cursor.fetchone()
        
        conn.close()
        
        if latest_borrow:
            return jsonify({
                'success': True,
                'borrow': {
                    'book_number': latest_borrow[0],
                    'book_name': latest_borrow[1],
                    'borrow_time': latest_borrow[2],
                    'due_date': latest_borrow[3],
                    'status': latest_borrow[4]
                }
            })
        else:
            return jsonify({'success': False, 'message': '暂无借阅记录'})
            
    except Exception as e:
        print(f"获取最新借阅记录出错: {e}")
        return jsonify({'success': False, 'message': f'获取记录失败：{str(e)}'}), 500

# 读者借阅状态检查API
@app.route('/api/reader/borrow/status')
@login_required
def reader_borrow_status_api():
    if session.get('user_type') != 'reader':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        reader_id = session.get('user_id')
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 获取读者基本信息
        cursor.execute('''
            SELECT r.CNo, r.RFine, bc.CW, bc.CNum
            FROM reader r
            LEFT JOIN bookcredit bc ON r.CNo = bc.CNo
            WHERE r.RNo = ?
        ''', (reader_id,))
        
        reader_info = cursor.fetchone()
        
        if not reader_info:
            conn.close()
            return jsonify({'success': False, 'message': '读者信息不存在'}), 404
        
        card_number = reader_info[0]
        reader_fine = float(reader_info[1] or 0)
        card_status = reader_info[2]  # 0=正常，1=挂失
        max_borrow = reader_info[3] or 5
        
        # 获取当前借阅数量
        cursor.execute('SELECT COUNT(*) FROM borrow WHERE CNo = ? AND (BBBTime IS NULL OR BBBTime = "")', (card_number,))
        borrowed_count = cursor.fetchone()[0] or 0
        
        # 获取最近借阅记录
        cursor.execute('''
            SELECT b.BNo, bk.BName, b.BBTime, 
                   DATE(b.BBTime, '+30 days') as DueDate,
                   CASE 
                       WHEN b.BBBTime IS NULL OR b.BBBTime = '' THEN '在借'
                       ELSE '已还'
                   END as status
            FROM borrow b
            JOIN book bk ON b.BNo = bk.BNo
            WHERE b.CNo = ?
            ORDER BY b.BBTime DESC
            LIMIT 3
        ''', (card_number,))
        
        recent_borrows = cursor.fetchall()
        
        conn.close()
        
        # 格式化最近借阅记录
        borrows_list = []
        for borrow in recent_borrows:
            # 计算是否逾期
            is_overdue = False
            if borrow[2] and borrow[4] == '在借':
                try:
                    borrow_date = datetime.strptime(borrow[2], '%Y-%m-%d %H:%M:%S')
                    days_borrowed = (datetime.now() - borrow_date).days
                    is_overdue = days_borrowed > 30
                except:
                    pass
            
            borrows_list.append({
                'book_number': borrow[0],
                'book_name': borrow[1],
                'borrow_time': borrow[2],
                'due_date': borrow[3],
                'status': borrow[4],
                'is_overdue': is_overdue
            })
        
        return jsonify({
            'success': True,
            'status': {
                'can_borrow': card_status == '0' and reader_fine == 0,
                'card_status': '正常' if card_status == '0' else '挂失',
                'unpaid_fine': reader_fine,
                'max_borrow': max_borrow,
                'current_borrow': borrowed_count,
                'remaining_quota': max_borrow - borrowed_count
            },
            'recent_borrows': borrows_list
        })
        
    except Exception as e:
        print(f"获取读者借阅状态出错: {e}")
        return jsonify({'success': False, 'message': f'获取状态失败：{str(e)}'}), 500

# 罚款缴费页面
@app.route('/reader/fines')
@login_required
def reader_fines():
    if session.get('user_type') != 'reader':
        return redirect(url_for('login'))
    return render_template('reader_fines.html')

# 读者罚款记录API
@app.route('/api/reader/fines', methods=['GET'])
@login_required
def reader_fines_api():
    if session.get('user_type') != 'reader':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        reader_id = session.get('user_id')
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 获取读者的借阅卡号
        cursor.execute('SELECT CNo FROM reader WHERE RNo = ?', (reader_id,))
        reader_result = cursor.fetchone()
        
        if not reader_result:
            conn.close()
            return jsonify({'success': False, 'message': '读者信息不存在'}), 404
        
        card_number = reader_result[0]
        
        # 确保 fine 表和 fine_detail 表存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fine'")
        if not cursor.fetchone():
            # fine表不存在，创建它
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fine (
                    FNo CHAR(18) PRIMARY KEY,
                    CNo CHAR(12),
                    FTime DATETIME,
                    FFine NUMERIC(8,2)
                )
            ''')
            conn.commit()
        
        # 确保 fine_detail 表存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fine_detail'")
        if not cursor.fetchone():
            # fine_detail表不存在，创建它
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fine_detail (
                    FDNo VARCHAR(20) PRIMARY KEY,
                    FNo CHAR(18),
                    BNo VARCHAR(20),
                    Reason VARCHAR(100),
                    FineAmount NUMERIC(8,2),
                    FOREIGN KEY (FNo) REFERENCES fine(FNo),
                    FOREIGN KEY (BNo) REFERENCES book(BNo)
                )
            ''')
            conn.commit()
        
        # 查询罚款记录
        cursor.execute('''
            SELECT 
                f.FNo, 
                f.FTime, 
                f.FFine,
                GROUP_CONCAT(DISTINCT b.BName) as related_books,
                GROUP_CONCAT(DISTINCT fd.Reason) as reasons
            FROM fine f
            LEFT JOIN fine_detail fd ON f.FNo = fd.FNo
            LEFT JOIN book b ON fd.BNo = b.BNo
            WHERE f.CNo = ?
            GROUP BY f.FNo, f.FTime, f.FFine
            ORDER BY f.FTime DESC
        ''', (card_number,))
        
        fines = cursor.fetchall()
        
        # 查询总罚款金额 - 确保使用 fine 表中的数据
        cursor.execute('SELECT SUM(FFine) FROM fine WHERE CNo = ? AND FFine > 0', (card_number,))
        total_fine_result = cursor.fetchone()
        total_fine = float(total_fine_result[0]) if total_fine_result and total_fine_result[0] else 0.0
        
        # 查询未缴纳的罚款（金额大于0的罚款）
        cursor.execute('SELECT SUM(FFine) FROM fine WHERE CNo = ? AND FFine > 0', (card_number,))
        unpaid_fine_result = cursor.fetchone()
        unpaid_fine = float(unpaid_fine_result[0]) if unpaid_fine_result and unpaid_fine_result[0] else 0.0
        
        # 已缴纳的罚款（金额小于等于0的罚款）
        cursor.execute('SELECT COUNT(*) FROM fine WHERE CNo = ? AND FFine <= 0', (card_number,))
        paid_count_result = cursor.fetchone()
        paid_count = paid_count_result[0] if paid_count_result else 0
        
        # 同步罚款数据到 reader 表（确保一致性）
        cursor.execute('UPDATE reader SET RFine = ? WHERE CNo = ?', (unpaid_fine, card_number))
        cursor.execute('UPDATE bookcredit SET CFine = ? WHERE CNo = ?', (unpaid_fine, card_number))
        
        conn.commit()
        
        # 处理罚款记录
        fines_list = []
        for fine in fines:
            fine_number = fine[0]
            fine_date = fine[1]
            amount = float(fine[2] or 0)
            related_books = fine[3] if fine[3] else "未关联图书"
            reasons = fine[4] if fine[4] else "未说明原因"
            
            # 获取详细的罚款项目
            cursor.execute('''
                SELECT fd.Reason, b.BName, fd.FineAmount
                FROM fine_detail fd
                LEFT JOIN book b ON fd.BNo = b.BNo
                WHERE fd.FNo = ?
            ''', (fine_number,))
            
            fine_details = cursor.fetchall()
            details_list = []
            
            for detail in fine_details:
                details_list.append({
                    'reason': detail[0],
                    'book_name': detail[1] or '未知图书',
                    'amount': float(detail[2] or 0)
                })
            
            # 判断罚款状态（已缴纳：金额<=0）
            is_paid = amount <= 0
            status = '已缴清' if is_paid else '未缴纳'
            
            fines_list.append({
                'fine_number': fine_number,
                'fine_date': fine_date,
                'amount': amount,
                'status': status,
                'is_paid': is_paid,
                'related_books': related_books,
                'reasons': reasons,
                'details': details_list
            })
        
        # 统计信息
        unpaid_count = len([f for f in fines_list if not f['is_paid']])
        total_fines_count = len(fines_list)
        
        stats = {
            'total_fines': total_fines_count,
            'total_amount': total_fine,
            'unpaid_amount': unpaid_fine,
            'paid_count': paid_count,
            'unpaid_count': unpaid_count,
            'paid_percentage': round((paid_count / total_fines_count * 100), 1) if total_fines_count > 0 else 0
        }
        
        conn.close()
        
        return jsonify({
            'success': True, 
            'fines': fines_list,
            'stats': stats
        })
        
    except Exception as e:
        print(f"获取读者罚款记录出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'获取记录失败: {str(e)}'}), 500

# 缴纳罚款API
@app.route('/api/reader/fines/pay', methods=['POST'])
@login_required
def pay_fine_api():
    if session.get('user_type') != 'reader':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        data = request.json
        fine_number = data.get('fine_number')
        payment_amount = float(data.get('payment_amount', 0))
        
        if payment_amount <= 0:
            return jsonify({'success': False, 'message': '缴费金额必须大于0'}), 400
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 获取罚款信息
        cursor.execute('SELECT CNo, FFine FROM fine WHERE FNo = ?', (fine_number,))
        fine_info = cursor.fetchone()
        
        if not fine_info:
            conn.close()
            return jsonify({'success': False, 'message': '罚款记录不存在'}), 404
        
        card_number = fine_info[0]
        fine_amount = float(fine_info[1] or 0)
        
        # 检查读者信息
        cursor.execute('SELECT RNo, RFine FROM reader WHERE CNo = ?', (card_number,))
        reader_info = cursor.fetchone()
        
        if not reader_info:
            conn.close()
            return jsonify({'success': False, 'message': '读者信息不存在'}), 404
        
        reader_id = reader_info[0]
        reader_fine = float(reader_info[1] or 0)
        
        # 验证缴费金额
        if payment_amount > fine_amount:
            return jsonify({'success': False, 'message': f'缴费金额不能超过罚款金额¥{fine_amount}'}), 400
        
        # 更新罚款记录
        new_fine_amount = fine_amount - payment_amount
        cursor.execute('UPDATE fine SET FFine = ? WHERE FNo = ?', (new_fine_amount, fine_number))
        
        # 重新计算读者所有未缴罚款总额（确保数据同步）
        cursor.execute('SELECT SUM(FFine) FROM fine WHERE CNo = ? AND FFine > 0', (card_number,))
        total_unpaid_result = cursor.fetchone()
        new_total_unpaid = float(total_unpaid_result[0]) if total_unpaid_result and total_unpaid_result[0] else 0.0
        
        # 更新读者罚款金额（使用新的总未缴金额）
        cursor.execute('UPDATE reader SET RFine = ? WHERE RNo = ?', (new_total_unpaid, reader_id))
        
        # 更新书卡罚款金额
        cursor.execute('UPDATE bookcredit SET CFine = ? WHERE CNo = ?', (new_total_unpaid, card_number))
        
        conn.commit()
        
        # 记录缴费历史（需要创建缴费记录表）
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payment (
                    PNo VARCHAR(20) PRIMARY KEY,
                    FNo CHAR(18),
                    PTime DATETIME,
                    PAmount NUMERIC(8,2),
                    FOREIGN KEY (FNo) REFERENCES fine(FNo)
                )
            ''')
            
            # 生成缴费单号
            cursor.execute('SELECT MAX(CAST(SUBSTR(PNo, 2) AS INTEGER)) FROM payment WHERE PNo LIKE "P%"')
            max_pno_result = cursor.fetchone()
            max_pno = max_pno_result[0] if max_pno_result[0] else 0
            payment_no = f"P{max_pno + 1:03d}"
            
            cursor.execute('''
                INSERT INTO payment (PNo, FNo, PTime, PAmount)
                VALUES (?, ?, datetime('now'), ?)
            ''', (payment_no, fine_number, payment_amount))
            
            conn.commit()
        except Exception as e:
            print(f"创建缴费记录出错: {e}")
        
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'缴费成功！缴纳金额：¥{payment_amount:.2f}',
            'remaining_fine': new_fine_amount,
            'total_unpaid': new_total_unpaid
        })
        
    except Exception as e:
        print(f"缴纳罚款出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'缴费失败: {str(e)}'}), 500
    
# 个人信息页面
@app.route('/reader/profile')
@login_required
def reader_profile():
    if session.get('user_type') != 'reader':
        return redirect(url_for('login'))
    return render_template('reader_profile.html')

# 读者个人信息API
@app.route('/api/reader/profile', methods=['GET', 'PUT'])
@login_required
def reader_profile_api():
    if session.get('user_type') != 'reader':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        reader_id = session.get('user_id')
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        if request.method == 'GET':
            # 获取读者信息
            cursor.execute('''
                SELECT RNo, CNo, RName, RSex, RIDNum, RFine, username
                FROM reader 
                WHERE RNo = ?
            ''', (reader_id,))
            
            reader = cursor.fetchone()
            
            if not reader:
                conn.close()
                return jsonify({'success': False, 'message': '读者信息不存在'}), 404
            
            card_number = reader[1]
            
            # 同步罚款数据（确保罚款金额是最新的）
            cursor.execute('SELECT SUM(FFine) FROM fine WHERE CNo = ? AND FFine > 0', (card_number,))
            fine_total_result = cursor.fetchone()
            fine_total = float(fine_total_result[0]) if fine_total_result and fine_total_result[0] else 0.0
            
            # 如果 fine 表的罚款金额与 reader 表不一致，更新 reader 表
            if float(reader[5] or 0) != fine_total:
                cursor.execute('UPDATE reader SET RFine = ? WHERE RNo = ?', (fine_total, reader_id))
                cursor.execute('UPDATE bookcredit SET CFine = ? WHERE CNo = ?', (fine_total, card_number))
                conn.commit()
            
            # 获取借阅卡信息
            cursor.execute('''
                SELECT CNum, CW, CDate, Crenew
                FROM bookcredit
                WHERE CNo = ?
            ''', (card_number,))
            
            card_info = cursor.fetchone()
            
            # 获取借阅统计
            cursor.execute('SELECT COUNT(*) FROM borrow WHERE CNo = ? AND (BBBTime IS NULL OR BBBTime = "")', (card_number,))
            borrowed_count = cursor.fetchone()[0] or 0
            
            conn.close()
            
            reader_info = {
                'reader_number': reader[0],
                'card_number': reader[1],
                'name': reader[2],
                'gender': reader[3],
                'id_number': reader[4],
                'fine': fine_total,  # 使用同步后的罚款金额
                'username': reader[6],
                'borrowed_books': borrowed_count,
                'can_borrow_books': card_info[0] if card_info else 5,
                'card_status': '挂失' if card_info and card_info[1] == '1' else '正常',
                'card_date': card_info[2] if card_info else '',
                'renew_date': card_info[3] if card_info else '',
            }
            
            return jsonify({'success': True, 'profile': reader_info})
            
        elif request.method == 'PUT':
            # 更新读者信息
            data = request.json
            
            # 只能更新部分信息
            update_fields = []
            update_values = []
            
            if 'password' in data and data['password']:
                new_password = data['password'].strip()
                if len(new_password) >= 6:
                    update_fields.append('password = ?')
                    update_values.append(new_password)
                else:
                    conn.close()
                    return jsonify({'success': False, 'message': '密码长度至少6位'}), 400

            if update_fields:
                update_query = f'UPDATE reader SET {", ".join(update_fields)} WHERE RNo = ?'
                update_values.append(reader_id)
                cursor.execute(update_query, update_values)
                
                conn.commit()
                conn.close()
                
                return jsonify({'success': True, 'message': '个人信息更新成功'})
            else:
                conn.close()
                return jsonify({'success': False, 'message': '没有需要更新的信息'}), 400
            
    except Exception as e:
        print(f"读者个人信息操作出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

# 借阅卡管理页面
@app.route('/reader/card')
@login_required
def reader_card():
    if session.get('user_type') != 'reader':
        return redirect(url_for('login'))
    return render_template('reader_card.html')

# 读者借阅卡管理API
@app.route('/api/reader/card', methods=['GET', 'POST'])
@login_required
def reader_card_api():
    if session.get('user_type') != 'reader':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        reader_id = session.get('user_id')
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 获取读者的借阅卡号
        cursor.execute('SELECT CNo FROM reader WHERE RNo = ?', (reader_id,))
        reader_result = cursor.fetchone()
        
        if not reader_result:
            conn.close()
            return jsonify({'success': False, 'message': '读者信息不存在'}), 404
        
        card_number = reader_result[0]
        
        if request.method == 'GET':
            # 获取借阅卡信息
            cursor.execute('''
                SELECT CNum, CW, CDate, Crenew, CFine,
                       (SELECT COUNT(*) FROM borrow WHERE CNo = ? AND (BBBTime IS NULL OR BBBTime = '')) as borrowed_count
                FROM bookcredit
                WHERE CNo = ?
            ''', (card_number, card_number))
            
            card_info = cursor.fetchone()
            
            if not card_info:
                conn.close()
                return jsonify({'success': False, 'message': '借阅卡信息不存在'}), 404
            
            # 获取读者信息
            cursor.execute('SELECT RName, RFine FROM reader WHERE RNo = ?', (reader_id,))
            reader_info = cursor.fetchone()
            
            conn.close()
            
            card_data = {
                'card_number': card_number,
                'card_status': '挂失' if card_info[1] == '1' else '正常',
                'can_borrow_books': card_info[0],
                'current_borrowed': card_info[5] or 0,
                'card_date': card_info[2],
                'renew_date': card_info[3],
                'card_fine': float(card_info[4] or 0),
                'reader_fine': float(reader_info[1] or 0) if reader_info else 0,
                'reader_name': reader_info[0] if reader_info else ''
            }
            
            return jsonify({'success': True, 'card': card_data})
            
        elif request.method == 'POST':
            # 处理借阅卡操作
            data = request.json
            action = data.get('action')
            
            if action == 'renew':
                # 卡片续期
                renew_years = int(data.get('renew_years', 1))
                
                # 计算新的续期日期
                cursor.execute('SELECT Crenew FROM bookcredit WHERE CNo = ?', (card_number,))
                current_renew = cursor.fetchone()
                
                if current_renew and current_renew[0]:
                    # 在当前续期日期上增加年限
                    new_renew_date = datetime.strptime(current_renew[0], '%Y-%m-%d %H:%M:%S')
                    new_renew_date = new_renew_date.replace(year=new_renew_date.year + renew_years)
                    new_renew_str = new_renew_date.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    # 如果当前没有续期日期，从办卡日期开始计算
                    cursor.execute('SELECT CDate FROM bookcredit WHERE CNo = ?', (card_number,))
                    card_date = cursor.fetchone()
                    if card_date and card_date[0]:
                        card_date_obj = datetime.strptime(card_date[0], '%Y-%m-%d %H:%M:%S')
                        new_renew_date = card_date_obj.replace(year=card_date_obj.year + renew_years)
                        new_renew_str = new_renew_date.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        # 使用当前日期
                        new_renew_date = datetime.now().replace(year=datetime.now().year + renew_years)
                        new_renew_str = new_renew_date.strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute('UPDATE bookcredit SET Crenew = ? WHERE CNo = ?', 
                              (new_renew_str, card_number))
                
                conn.commit()
                conn.close()
                
                return jsonify({
                    'success': True, 
                    'message': f'借阅卡续期成功！新的有效期至：{new_renew_str}',
                    'new_renew_date': new_renew_str
                })
                
            elif action == 'toggle_lost':
                # 切换挂失状态
                cursor.execute('SELECT CW FROM bookcredit WHERE CNo = ?', (card_number,))
                current_status = cursor.fetchone()
                
                if not current_status:
                    conn.close()
                    return jsonify({'success': False, 'message': '借阅卡信息不存在'}), 404
                
                new_status = '0' if current_status[0] == '1' else '1'
                status_text = '挂失' if new_status == '1' else '解挂'
                
                cursor.execute('UPDATE bookcredit SET CW = ? WHERE CNo = ?', (new_status, card_number))
                
                conn.commit()
                conn.close()
                
                return jsonify({
                    'success': True, 
                    'message': f'借阅卡{status_text}成功',
                    'new_status': status_text
                })
                
            else:
                conn.close()
                return jsonify({'success': False, 'message': '无效的操作'}), 400
            
    except Exception as e:
        print(f"借阅卡管理操作出错: {e}")
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

# 借阅统计页面
@app.route('/reader/stats')
@login_required
def reader_stats():
    if session.get('user_type') != 'reader':
        return redirect(url_for('login'))
    return render_template('reader_stats.html')

# 读者借阅统计API
@app.route('/api/reader/stats', methods=['GET'])
@login_required
def reader_stats_api():
    if session.get('user_type') != 'reader':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        reader_id = session.get('user_id')
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 获取读者的借阅卡号
        cursor.execute('SELECT CNo FROM reader WHERE RNo = ?', (reader_id,))
        reader_result = cursor.fetchone()
        
        if not reader_result:
            conn.close()
            return jsonify({'success': False, 'message': '读者信息不存在'}), 404
        
        card_number = reader_result[0]

        # === 基本统计数据 ===
        # 总借阅量
        try:
            cursor.execute('SELECT COUNT(*) FROM borrow WHERE CNo = ?', (card_number,))
            total_borrows = cursor.fetchone()[0] or 0
        except Exception as e:
            print(f"查询总借阅量出错: {e}")
            total_borrows = 0
        
        # 当前借阅
        try:
            cursor.execute('SELECT COUNT(*) FROM borrow WHERE CNo = ? AND (BBBTime IS NULL OR BBBTime = "")', (card_number,))
            current_borrows = cursor.fetchone()[0] or 0
        except Exception as e:
            print(f"查询当前借阅出错: {e}")
            current_borrows = 0
        
        # 已还图书
        try:
            cursor.execute('SELECT COUNT(*) FROM borrow WHERE CNo = ? AND BBBTime IS NOT NULL', (card_number,))
            returned_books = cursor.fetchone()[0] or 0
        except Exception as e:
            print(f"查询已还图书出错: {e}")
            returned_books = 0
        
        # 逾期次数
        try:
            cursor.execute('''
                SELECT COUNT(*) FROM borrow 
                WHERE CNo = ? 
                AND BBBTime IS NULL 
                AND julianday("now") - julianday(BBTime) > 30
            ''', (card_number,))
            overdue_count = cursor.fetchone()[0] or 0
        except Exception as e:
            print(f"查询逾期次数出错: {e}")
            overdue_count = 0
        
        # === 月度借阅统计 ===
        monthly_data = [0] * 12
        try:
            cursor.execute('''
                SELECT strftime('%m', BBTime) as month, COUNT(*) as count
                FROM borrow
                WHERE CNo = ? AND strftime('%Y', BBTime) = strftime('%Y', 'now')
                GROUP BY strftime('%m', BBTime)
                ORDER BY month
            ''', (card_number,))
            
            monthly_stats = cursor.fetchall()
            
            for stat in monthly_stats:
                month_index = int(stat[0]) - 1
                monthly_data[month_index] = stat[1]
        except Exception as e:
            print(f"查询月度统计出错: {e}")
        
        # === 最喜欢的图书类型 ===
        book_type_data = []
        try:
            cursor.execute('''
                SELECT bt.BTName, COUNT(*) as count
                FROM borrow b
                JOIN book bk ON b.BNo = bk.BNo
                JOIN booktype bt ON bk.BTNo = bt.BTNo
                WHERE b.CNo = ?
                GROUP BY bk.BTNo
                ORDER BY count DESC
                LIMIT 5
            ''', (card_number,))
            
            book_type_stats = cursor.fetchall()
            
            # 计算百分比
            total_by_type = sum([stat[1] for stat in book_type_stats])
            for stat in book_type_stats:
                percentage = (stat[1] / total_by_type * 100) if total_by_type > 0 else 0
                book_type_data.append({
                    'name': stat[0],
                    'count': stat[1],
                    'percentage': round(percentage, 1)
                })
        except Exception as e:
            print(f"查询图书类型统计出错: {e}")
        
        # === 借阅时间段分布 ===
        time_data = []
        try:
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN CAST(strftime('%H', BBTime) AS INTEGER) BETWEEN 8 AND 12 THEN '工作日白天 (8-12点)'
                        WHEN CAST(strftime('%H', BBTime) AS INTEGER) BETWEEN 14 AND 18 THEN '工作日白天 (14-18点)'
                        WHEN CAST(strftime('%H', BBTime) AS INTEGER) BETWEEN 19 AND 22 THEN '晚上 (19-22点)'
                        WHEN CAST(strftime('%w', BBTime) AS INTEGER) IN (0, 6) THEN '周末'
                        ELSE '其他时间'
                    END as time_period,
                    COUNT(*) as count
                FROM borrow
                WHERE CNo = ? AND BBTime IS NOT NULL
                GROUP BY time_period
                ORDER BY count DESC
            ''', (card_number,))
            
            time_stats = cursor.fetchall()
            
            # 计算百分比
            total_time = sum([stat[1] for stat in time_stats])
            for stat in time_stats:
                percentage = (stat[1] / total_time * 100) if total_time > 0 else 0
                time_data.append({
                    'period': stat[0],
                    'count': stat[1],
                    'percentage': round(percentage, 1)
                })
        except Exception as e:
            print(f"查询时间段统计出错: {e}")
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_borrows': total_borrows,
                'current_borrows': current_borrows,
                'returned_books': returned_books,
                'overdue_count': overdue_count
            },
            'monthly_data': monthly_data,
            'book_type_stats': book_type_data,
            'time_stats': time_data
        })
        
    except Exception as e:
        print(f"获取读者统计信息出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'获取统计信息失败: {str(e)}'}), 500

# 读者注册路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        gender = request.form.get('gender')
        id_number = request.form.get('id_number')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # 验证必填字段
        if not all([username, password, name, gender, id_number]):
            return render_template('register.html', error='请填写所有必填字段')
        
        if len(password) < 6:
            return render_template('register.html', error='密码长度至少6位')
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        try:
            # 检查用户名是否已存在
            cursor.execute('SELECT username FROM reader WHERE username = ?', (username,))
            if cursor.fetchone():
                conn.close()
                return render_template('register.html', error='用户名已存在')
            
            # 检查身份证号是否已存在
            cursor.execute('SELECT RIDNum FROM reader WHERE RIDNum = ?', (id_number,))
            if cursor.fetchone():
                conn.close()
                return render_template('register.html', error='身份证号已注册')
            
            # 生成读者编号 - 从 reader 表获取最大值
            cursor.execute('SELECT MAX(CAST(SUBSTR(RNo, 2) AS INTEGER)) FROM reader WHERE RNo LIKE "R%"')
            max_rno_result = cursor.fetchone()
            max_rno = max_rno_result[0] if max_rno_result[0] else 0
            new_rno = f"R{max_rno + 1:03d}"
            
            # 生成借阅卡号 - 从 bookcredit 表获取最大值
            cursor.execute('SELECT MAX(CAST(SUBSTR(CNo, 2) AS INTEGER)) FROM bookcredit WHERE CNo LIKE "C%"')
            max_cno_result = cursor.fetchone()
            max_cno = max_cno_result[0] if max_cno_result[0] else 0
            new_cno = f"C{max_cno + 1:03d}"
            
            print(f"[DEBUG] 生成读者编号: {new_rno}, 借阅卡号: {new_cno}")
            
            # 插入读者数据
            cursor.execute('''
                INSERT INTO reader (RNo, CNo, RName, RSex, RIDNum, RFine, username, password)
                VALUES (?, ?, ?, ?, ?, 0.0, ?, ?)
            ''', (new_rno, new_cno, name, gender, id_number, username, password))
            
            # 创建借阅卡记录
            cursor.execute('''
                INSERT INTO bookcredit (CNo, RNo, CFine, CNum, CW, CDate, Crenew)
                VALUES (?, ?, 0.0, 5, '0', datetime('now'), datetime('now', '+1 year'))
            ''', (new_cno, new_rno))
            
            conn.commit()
            conn.close()
            
            # 注册成功后自动登录
            session['user_type'] = 'reader'
            session['username'] = name
            session['user_id'] = new_rno
            
            return redirect(url_for('reader_dashboard'))
            
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"注册出错: {e}")
            return render_template('register.html', error='注册失败，请稍后重试')
    
    return render_template('register.html')

# 读者注册成功页面
@app.route('/register/success')
def register_success():
    if 'user_type' not in session or session.get('user_type') != 'reader':
        return redirect(url_for('login'))
    return render_template('register_success.html')

# 读者图书搜索API
@app.route('/api/reader/search/books', methods=['GET'])
@login_required
def reader_search_books_api():
    if session.get('user_type') != 'reader':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        search_type = request.args.get('search_type', 'name')
        search_value = request.args.get('search_value', '')
        
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        if search_type == 'name':
            cursor.execute('''
                SELECT b.BNo, b.BName, b.BAuthor, bt.BTName, p.PName, b.Price, b.TotalNum, b.Biomass
                FROM book b
                LEFT JOIN booktype bt ON b.BTNo = bt.BTNo
                LEFT JOIN publisher p ON b.PNo = p.PNo
                WHERE b.BName LIKE ?
                ORDER BY b.BName
            ''', ('%' + search_value + '%',))
        elif search_type == 'author':
            cursor.execute('''
                SELECT b.BNo, b.BName, b.BAuthor, bt.BTName, p.PName, b.Price, b.TotalNum, b.Biomass
                FROM book b
                LEFT JOIN booktype bt ON b.BTNo = bt.BTNo
                LEFT JOIN publisher p ON b.PNo = p.PNo
                WHERE b.BAuthor LIKE ?
                ORDER BY b.BName
            ''', ('%' + search_value + '%',))
        elif search_type == 'type':
            cursor.execute('''
                SELECT b.BNo, b.BName, b.BAuthor, bt.BTName, p.PName, b.Price, b.TotalNum, b.Biomass
                FROM book b
                LEFT JOIN booktype bt ON b.BTNo = bt.BTNo
                LEFT JOIN publisher p ON b.PNo = p.PNo
                WHERE bt.BTName LIKE ?
                ORDER BY b.BName
            ''', ('%' + search_value + '%',))
        elif search_type == 'publisher':
            cursor.execute('''
                SELECT b.BNo, b.BName, b.BAuthor, bt.BTName, p.PName, b.Price, b.TotalNum, b.Biomass
                FROM book b
                LEFT JOIN booktype bt ON b.BTNo = bt.BTNo
                LEFT JOIN publisher p ON b.PNo = p.PNo
                WHERE p.PName LIKE ?
                ORDER BY b.BName
            ''', ('%' + search_value + '%',))
        else:
            # 默认返回所有图书
            cursor.execute('''
                SELECT b.BNo, b.BName, b.BAuthor, bt.BTName, p.PName, b.Price, b.TotalNum, b.Biomass
                FROM book b
                LEFT JOIN booktype bt ON b.BTNo = bt.BTNo
                LEFT JOIN publisher p ON b.PNo = p.PNo
                ORDER BY b.BName
                LIMIT 50
            ''')
        
        books = cursor.fetchall()
        conn.close()
        
        books_list = []
        for book in books:
            books_list.append({
                'book_number': book[0],
                'book_name': book[1],
                'author': book[2],
                'type': book[3],
                'publisher': book[4],
                'price': book[5],
                'total_num': book[6],
                'available_num': book[7],
                'can_borrow': book[7] > 0  # 有库存才能借
            })
        
        return jsonify({'success': True, 'books': books_list})
        
    except Exception as e:
        print(f"读者搜索图书出错: {e}")
        return jsonify({'success': False, 'message': f'搜索失败: {str(e)}'}), 500


# 测试路由 - 用于调试
@app.route('/api/debug/readers')
@login_required
def debug_readers():
    if session.get('user_type') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'})
    
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # 获取所有读者
    cursor.execute('SELECT RNo, RName, CNo FROM reader LIMIT 10')
    readers = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'readers': [{'reader_number': r[0], 'reader_name': r[1], 'card_number': r[2]} for r in readers]
    })

# 读者热门图书API
@app.route('/api/reader/popular-books', methods=['GET'])
@login_required
def reader_popular_books_api():
    if session.get('user_type') != 'reader':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 查询借阅次数最多的图书
        cursor.execute('''
            SELECT b.BNo, b.BName, b.BAuthor, b.Biomass,
                   COUNT(bw.BNo) as borrow_count
            FROM book b
            LEFT JOIN borrow bw ON b.BNo = bw.BNo
            GROUP BY b.BNo
            ORDER BY borrow_count DESC, b.BName
            LIMIT 6
        ''')
        
        books = cursor.fetchall()
        conn.close()
        
        books_list = []
        for book in books:
            books_list.append({
                'BNo': book[0],
                'BName': book[1],
                'BAuthor': book[2],
                'Biomass': book[3],
                'borrow_count': book[4] or 0
            })
        
        return jsonify({'success': True, 'books': books_list})
        
    except Exception as e:
        print(f"获取热门图书出错: {e}")
        return jsonify({'success': False, 'message': f'获取数据失败: {str(e)}'}), 500

# 读者新书推荐API
@app.route('/api/reader/new-books', methods=['GET'])
@login_required
def reader_new_books_api():
    if session.get('user_type') != 'reader':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # 查询最近入库的图书
        cursor.execute('''
            SELECT BNo, BName, BAuthor, Biomass, InputTime
            FROM book
            ORDER BY InputTime DESC
            LIMIT 6
        ''')
        
        books = cursor.fetchall()
        conn.close()
        
        books_list = []
        for book in books:
            # 格式化日期
            input_time = book[4]
            if input_time:
                try:
                    # 尝试解析日期
                    dt = datetime.strptime(input_time, '%Y-%m-%d %H:%M:%S')
                    formatted_date = dt.strftime('%Y年%m月%d日')
                except:
                    formatted_date = input_time
            else:
                formatted_date = '未知'
            
            books_list.append({
                'BNo': book[0],
                'BName': book[1],
                'BAuthor': book[2],
                'Biomass': book[3],
                'InputTime': formatted_date
            })
        
        return jsonify({'success': True, 'books': books_list})
        
    except Exception as e:
        print(f"获取新书推荐出错: {e}")
        return jsonify({'success': False, 'message': f'获取数据失败: {str(e)}'}), 500

# 修改现有的读者搜索路由，使其支持模板渲染
@app.route('/reader/search')
@login_required
def reader_search():
    if session.get('user_type') != 'reader':
        return redirect(url_for('login'))
    
    # 获取搜索参数
    search_type = request.args.get('search_type', 'name')
    search_value = request.args.get('search_value', '')
    
    books = []
    
    if search_value:
        # 执行搜索
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        if search_type == 'name':
            cursor.execute('''
                SELECT b.BNo, b.BName, b.BAuthor, bt.BTName, p.PName, b.Price, b.TotalNum, b.Biomass
                FROM book b
                LEFT JOIN booktype bt ON b.BTNo = bt.BTNo
                LEFT JOIN publisher p ON b.PNo = p.PNo
                WHERE b.BName LIKE ?
                ORDER BY b.BName
            ''', ('%' + search_value + '%',))
        elif search_type == 'author':
            cursor.execute('''
                SELECT b.BNo, b.BName, b.BAuthor, bt.BTName, p.PName, b.Price, b.TotalNum, b.Biomass
                FROM book b
                LEFT JOIN booktype bt ON b.BTNo = bt.BTNo
                LEFT JOIN publisher p ON b.PNo = p.PNo
                WHERE b.BAuthor LIKE ?
                ORDER BY b.BName
            ''', ('%' + search_value + '%',))
        elif search_type == 'type':
            cursor.execute('''
                SELECT b.BNo, b.BName, b.BAuthor, bt.BTName, p.PName, b.Price, b.TotalNum, b.Biomass
                FROM book b
                LEFT JOIN booktype bt ON b.BTNo = bt.BTNo
                LEFT JOIN publisher p ON b.PNo = p.PNo
                WHERE bt.BTName LIKE ?
                ORDER BY b.BName
            ''', ('%' + search_value + '%',))
        elif search_type == 'publisher':
            cursor.execute('''
                SELECT b.BNo, b.BName, b.BAuthor, bt.BTName, p.PName, b.Price, b.TotalNum, b.Biomass
                FROM book b
                LEFT JOIN booktype bt ON b.BTNo = bt.BTNo
                LEFT JOIN publisher p ON b.PNo = p.PNo
                WHERE p.PName LIKE ?
                ORDER BY b.BName
            ''', ('%' + search_value + '%',))
        elif search_type == 'all':
            # 搜索全部图书
            cursor.execute('''
                SELECT b.BNo, b.BName, b.BAuthor, bt.BTName, p.PName, b.Price, b.TotalNum, b.Biomass
                FROM book b
                LEFT JOIN booktype bt ON b.BTNo = bt.BTNo
                LEFT JOIN publisher p ON b.PNo = p.PNo
                ORDER BY b.BName
                LIMIT 50
            ''')
            # 如果搜索全部，清空搜索值显示
            search_value = ""
        
        books = cursor.fetchall()
        conn.close()
    
    return render_template('reader_search.html', 
                         search_type=search_type,
                         search_value=search_value,
                         books=books)

# 主程序
if __name__ == '__main__':
    init_db()
    create_views()
    create_triggers()
    app.run(debug=True, host='0.0.0.0', port=5000)
