TIME_ZONE = 'Asia/Yekaterinburg'

HELP_TEXT = (
    'Команды для пользователей:\n'
    '/terms - Термины и определения\n'
    '/key_rules - Ключевые правила безопасности\n'
    '/vnimanie - Информационные листы ВНИМАНИЕ\n'
    '/answers - Ответы на билеты по отдельным вопросам\n'
    '/tickets - Ответы на билеты одним файлом\n'
    '/my_stats - Статистика проверки знаний\n\n'
    'Команды для администраторов:\n'
    '/unsolve_test - Пользователи, не прошедшие тестирование\n'
    '/users_stats - Просмотр статистики пользователей\n'
    '/export_tests - Экспорт тестовых вопросов в docx-файл\n'
    '/report - Экспорт квартального отчёта о прохождении тестирования в pdf-файл\n'
    '/results - Экспорт результатов тестирования в docx-файл'
)

DEPARTMENTS = {
    'ГКС': ('КЦ-1,4', 'КЦ-2,3', 'КЦ-5,6', 'КЦ-7,8', 'КЦ-9,10',),
    'ЛЭС': (),
    'ЭВС': (
        'Участок по эксплуатации ТВС и К ЛПУМГ',
        'Группа по эксплуатации газоиспользующего оборудования ЛПУМГ',
        'Участок ТО и Р оборудования электроснабжения ЛПУМГ',
        'Участок электростанции собственных нужд'
    ),
    'Служба ЗК': (),
    'Служба АиМО': (),
    'Служба связи': (),
    'ВПО': (),
    'Служба ХМТРиСО': (),
}

INITIAL_TEXT = 'Для начала работы пройдите регистрацию \n\n/registration'

WORK_CODES = {
    'ozp': (
        'Работы по подготовке объектов к осенне-зимней эксплуатации',
        'Подготовка к осенне-зимнему периоду',
        ':snowflake:',
    ),
    'pozh': (
        'Работы по подготовке объектов к пожароопасному периоду',
        'Подготовка к пожароопасному периоду',
        ':fire:',
    ),
    'voda': (
        'Работы по подготовке объектов к работе в условиях весеннего паводка',
        'Подготовка к весеннему паводку',
        ':water_wave:',
    ),
    'hoz': (
        'Работы, выполняемые хозяйственным способом',
        'Работы, выполняемые хоз.способом',
        ':safety_vest:',
    ),
}
