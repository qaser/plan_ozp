from math import ceil

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config.mongo_config import works
from keyboards.for_stats import get_exit_kb

router = Router()


@router.message(Command('stats'))
async def send_stats(message: Message):
    pipeline_dep_done = [
        {'$match': {'is_done': 'Выполнено'}},
        {'$group': {'_id': '$department', 'count': {'$sum': 1}}},
    ]
    pipeline_dep_all = [
        {'$group': {'_id': '$department', 'count': {'$sum': 1}}},
    ]
    pipeline_type_done = [
        {'$match': {'is_done': 'Выполнено'}},
        {'$group': {'_id': '$type', 'count': {'$sum': 1}}},
    ]
    pipeline_type_all = [
        {'$group': {'_id': '$type', 'count': {'$sum': 1}}},
    ]
    sum_all = works.count_documents({})
    sum_done = works.count_documents({'is_done': 'Выполнено'})
    sum_percent = ceil((sum_done / sum_all) * 100)
    sum_text = f'Выполнено мероприятий: {sum_done} из {sum_all} ({sum_percent}%)'
    res_dep_all = list(works.aggregate(pipeline_dep_all))
    res_dep_done = list(works.aggregate(pipeline_dep_done))
    res_type_all = list(works.aggregate(pipeline_type_all))
    res_type_done = list(works.aggregate(pipeline_type_done))
    dict_dep = concat_lists(res_dep_all, res_dep_done)
    dict_type = concat_lists(res_type_all, res_type_done)
    dep_text = generate_text_from_dict(dict_dep)
    type_text = generate_text_from_dict(dict_type)
    await message.delete()
    await message.answer(
        f'<u>Статистика выполнения мероприятий</u>\n{sum_text}\n\n{dep_text}\n{type_text}',
        reply_markup=get_exit_kb(),
        parse_mode='HTML'
    )


def concat_lists(list_all, list_done):
    res_dict = {}
    for i in list_all:
        res_dict[i.get('_id')] = [i.get('count'), 0]
    for i in list_done:
        res_dict[i.get('_id')][1] = i.get('count')
    return res_dict


def generate_text_from_dict(res_dict):
    res_text = ''
    for name, counts in res_dict.items():
        count_all, count_done = counts
        count_percent = ceil((count_done / count_all) * 100)
        text = f'<b>{name}</b>: {count_done} из {count_all} ({count_percent}%)\n'
        res_text = f'{res_text}{text}'
    return res_text
