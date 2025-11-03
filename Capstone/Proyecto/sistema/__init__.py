# sistema/__init__.py
"""
PyMySQL como reemplazo de MySQLdb para Django.
Esto permite usar ENGINE='django.db.backends.mysql' con el driver PyMySQL.
"""

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception as exc:
    # No interrumpir import; Django fallará más adelante con error claro si PyMySQL no está.
    # Útil cuando se ejecutan comandos que no llegan a tocar DB.
    pass
