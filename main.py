import vk_api
import logging
import schedule
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from database import *
from datetime import datetime
from random import randint
from threading import Thread
from time import sleep


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TOKEN = "f8e5c9233a9747a464451803569ca505e51caf23427e0e7a15c901710eab660e2087912bc11ca95e20177"
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()


def announce():
    questions_to_announce = session.query(Question).filter(
       and_(Question.announced == 0,
            Question.announce_time < datetime.now())
    ).all()
    if not questions_to_announce:
        return
    chats = set([u.group_id for u in session.query(User).all()])
    announcer = "Новые вопросы:\n\n"
    for q in questions_to_announce:
        q.announced = 1
        announcer += f"Вопрос {q.id}\n"
        announcer += f"\n\nНачало в {q.start_time}."
        announcer += f"\nОтвечать можно до {q.end_time}.\n\n"
    for chat in chats:
        vk.messages.send(peer_id=chat, message=announcer,
                         random_id=rndid())
    session.commit()


def announce_driver():
    schedule.every(10).seconds.do(announce)

    while True:
        schedule.run_pending()
        sleep(1)


thread = Thread(target=announce_driver)
thread.start()


def rndid():
    return randint(0, 2 ** 31 - 1)


def bot_is_called(event):
    text = event.object["message"]["text"].split()
    return len(text) > 1 and "@mplbot" in text[0]


def refers_to_current_task(text):
    try:
        arg = int(text[1])
    except ValueError or TypeError:
        return False
    else:
        current_time = datetime.now()
        question = session.query(Question).filter_by(id=arg).one_or_none()
        if question is not None and question.start_time <= current_time <= question.end_time:
            return True
        return False


def print_best_players(event):
    top = 10
    current_group = event.object["message"]["peer_id"]
    players = session.query(User).filter(
        and_(User.group_id == current_group,
             User.points != 0)
    ).all()
    players.sort(key=lambda player: player.points)
    players = players[:top]
    answer = "Лучшие игроки этого чата:\n\n" if players else "Пока здесь никто не играл."
    for p in range(len(players)):
        info = vk.users.get(user_ids=players[p].vk_id)[0]
        answer += f"{p + 1}. {info['first_name']} {info['last_name']}: {players[p].points} баллов\n"
    vk.messages.send(peer_id=current_group, message=answer,
                     random_id=rndid())


def update_playerbase(event):
    data = event.object['message']
    player_exists = session.query(User).filter(
        and_(
            User.vk_id == data['from_id'],
            User.group_id == data['peer_id']
        )
    ).one_or_none()
    if player_exists is not None:
        return
    new_player = User(vk_id=data['from_id'], group_id=data['peer_id'], points=0, admin=False)
    session.add(new_player)
    session.commit()


def print_active_tasks(event):
    data = event.object['message']
    questions = session.query(Question).filter(and_(
        Question.start_time < datetime.now(),
        Question.end_time > datetime.now()
    )).all()
    solved = session.query(Solution).filter_by(group_id=data['peer_id']).all()
    solved = set([t.task_id for t in solved])

    questions = list(filter(lambda q: q.id not in solved, questions))
    answer = "Список активных вопросов:\n"

    if not questions:
        answer = "На данный момент нет ни одной активной задачи."

    for q in questions:
        answer += f"Вопрос {q.id}\n"
        answer += q.statement
        answer += f"\nОтвечать можно до {q.end_time}\n\n"
    vk.messages.send(peer_id=data['peer_id'], message=answer,
                     random_id=rndid())


keywords = {
    "best": print_best_players,
    "active": print_active_tasks
}


def check_answer_and_respond(event, message):
    data = event.object['message']
    task = session.query(Question).filter_by(id=int(message[1])).first()
    solution = session.query(Solution).filter(
        and_(
            Solution.task_id == task.id,
            Solution.group_id == data['peer_id']
        )
    ).one_or_none()
    if solution is None:  # (not yet!)
        correct = task.correct_answer == message[2].lower().strip()
        user = session.query(User).filter(
            and_(
                User.vk_id == data['from_id'],
                User.group_id == data['peer_id']
            )
        ).first()
        if correct:
            user.points += task.points
            new_solution = Solution(group_id=data['peer_id'], task_id=task.id)
            session.add(new_solution)
            session.commit()
            vk.messages.send(peer_id=data['peer_id'], message=f"Правильно! +{task.points} баллов",
                             random_id=rndid())
        else:
            vk.messages.send(peer_id=data['peer_id'], message="Неправильный ответ на тесте 1.",
                             random_id=rndid())
    else:
        vk.messages.send(peer_id=data['peer_id'], message="Эта задача уже решена.",
                         random_id=rndid())


def handle_new_message(event):
    chat_id = event.object['message']['peer_id']
    if chat_id < 2 * 10 ** 9:
        return
    text = event.object['message']['text'].split()
    update_playerbase(event)
    if not bot_is_called(event):
        return
    for keyword in keywords:
        if text[1].lower() == keyword:
            keywords[keyword](event)
    if not refers_to_current_task(text):
        return
    check_answer_and_respond(event, text)


def main():
    lp = VkBotLongPoll(vk_session, 194938806)
    for event in lp.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            handle_new_message(event)


main()
