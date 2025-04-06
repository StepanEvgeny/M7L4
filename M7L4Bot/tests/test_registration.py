import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users, user_choice, main
from registration import registration as reg
import builtins
from unittest.mock import patch, call

# Тест на неверный логин или пароль
from unittest.mock import patch, call

# Тест на неверный логин или пароль
@patch('registration.registration.display_users')
@patch('builtins.print')
@patch('builtins.input', side_effect=['3'])  # "3" – неверный выбор
def test_main_invalid_choice(mock_input, mock_print, mock_display_users):
    main()
    assert any("Неверный ввод" in str(call_arg) for call_arg in mock_print.call_args_list)


# ✅ Успешная авторизация
@patch('registration.registration.create_db')
@patch('registration.registration.display_users')
@patch('registration.registration.authenticate_user', return_value=True)
@patch('builtins.print')
@patch('builtins.input', side_effect=['1', 'testuser', 'password'])
def test_main_login_success(mock_input, mock_print, mock_auth, mock_display_users, mock_create_db):
    main()
    mock_auth.assert_called_once_with('testuser', 'password')
    mock_print.assert_any_call("Авторизация успешна.")


# ❌ Неуспешная авторизация
@patch('registration.registration.create_db')
@patch('registration.registration.display_users')
@patch('registration.registration.authenticate_user', return_value=False)
@patch('builtins.print')
@patch('builtins.input', side_effect=['1', 'wronguser', 'wrongpass'])
def test_main_login_fail(mock_input, mock_print, mock_auth, mock_display_users, mock_create_db):
    main()
    mock_auth.assert_called_once_with('wronguser', 'wrongpass')
    mock_print.assert_any_call("Неверный логин или пароль.")


# 🆕 Регистрация пользователя
@patch('registration.registration.create_db')
@patch('registration.registration.display_users')
@patch('registration.registration.add_user')
@patch('builtins.print')
@patch('builtins.input', side_effect=['2', 'newuser', 'email@example.com', 'newpass'])
def test_main_register_user(mock_input, mock_print, mock_add_user, mock_display_users, mock_create_db):
    main()
    mock_add_user.assert_called_once_with('newuser', 'email@example.com', 'newpass')

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."

# Возможные варианты тестов:
def test_add_existing_user(setup_database):
    add_user('duplicate', 'dup@example.com', '123')
    assert not add_user('duplicate', 'dup@example.com', '123')  # второй раз — ошибка

def test_authenticate_success(setup_database):
    add_user('authuser', 'auth@example.com', 'mypassword')
    assert authenticate_user('authuser', 'mypassword')

def test_authenticate_wrong_password(setup_database):
    assert not authenticate_user('authuser', 'wrongpassword')

def test_authenticate_nonexistent_user(setup_database):
    assert not authenticate_user('ghost', 'nopass')

def test_display_users_output(capsys, setup_database):
    add_user('showuser', 'show@example.com', 'pass')
    display_users()
    captured = capsys.readouterr()
    assert "Логин: showuser" in captured.out

def test_user_choice(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: '1')
    assert user_choice() == '1'


def test_main_login_success(monkeypatch):
    inputs = iter(['1', 'testuser', 'testpass'])

    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    monkeypatch.setattr(reg, 'authenticate_user', lambda u, p: True)
    monkeypatch.setattr(reg, 'create_db', lambda: None)
    monkeypatch.setattr(reg, 'display_users', lambda: None)
    monkeypatch.setattr('builtins.print', lambda *args, **kwargs: None)

    main()


def test_main_register(monkeypatch):
    inputs = iter(['2', 'newuser', 'email@example.com', 'newpass'])

    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    monkeypatch.setattr(reg, 'add_user', lambda u, e, p: None)
    monkeypatch.setattr(reg, 'create_db', lambda: None)
    monkeypatch.setattr(reg, 'display_users', lambda: None)
    monkeypatch.setattr('builtins.print', lambda *args, **kwargs: None)

    main()


def test_main_invalid_choice(monkeypatch, capsys):
    inputs = iter(['5'])  # Некорректный выбор
    monkeypatch.setattr(builtins, 'input', lambda _: next(inputs))

    main()

    captured = capsys.readouterr()
    assert "Неверный ввод" in captured.out


