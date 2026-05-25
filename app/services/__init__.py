import html
import re

import grpc
from loguru import logger
from songs import songs_pb2
from songs.songs_pb2_grpc import SongsServiceStub

from loader import _


async def get_song(
    songs: SongsServiceStub, user_id: str, id: str, source: songs_pb2.Source = songs_pb2.Source.HOLYCHORDS
) -> songs_pb2.Song:
    try:
        song = await songs.Get(songs_pb2.GetRequest(id=id, source=source), metadata=[("user_id", user_id)])
    except grpc.RpcError as e:
        logger.error(f"gRPC Error in select_song: {e.code()} - {e.details()}")

        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise Exception(_("Song not found"))
        raise Exception(_("Internal error"))

    return song


chord_regex = r"^[A-H][b#]?(2|5|6|7|9|11|13|\+|\+2|\+4|\+5|\+6|\+7|\+9|\+11|\+13|6/9|7-5|7-9|7#5|#5|7#9|#9|7+3|7+5|7+9|7b5|7b9|7sus2|7sus4|add2|add4|add6|add9|aug|dim|dim7|m/maj7|m6|m7|m7b5|m9|m11|m13|maj|maj7|maj9|maj11|maj13|mb5|m|sus|sus2|sus4|m7add11|add11|b5|-5|4)*(/[A-H][b#]*)*$"
videlit = (
    r"(1\|)|(2\|)|(3\|)|(4\|)|(5\|)|(6\|)|1:|2:|3:|4:|5:|6:|7:|8:|9:|0:|вступление:|интро:|куплет:|припев:|переход:|реп:|мост:|мостик:|вставка:|речитатив:|бридж:|инструментал:|проигрыш:|запев:|концовка:|окончание:|в конце:|кода:|тэг:|стих:|слово:|декла"
    "мация:|intro:|verse:|chorus:|bridge:|instrumental:|build:|ending:|link:|outro:|interlude:|rap:|spontaneous:|refrain:|tag:|coda:|vamp:|channel:|break:|breakdown:|hook:|turnaround:|turn:|solo:|вступ:|інтро:|приспів:|інструментал:|"
    "інтерлюдія:|брідж:|заспів:|міст:|програш:|соло:|перехід:|повтор:|кінець:|в кінці:|фінал:|кінцівка:|закінчення:|тег:|вірш:|частина:|прыпеў:|прысьпеў:|пройгрыш:|couplet:|pont:|strofă:|refren:|verso:|coro:|puente:|refrão:|parte:|strofa:|zwrotka:|espontáneo:|chords:"
)
chord_pattern = re.compile(chord_regex)
videlit_pattern = re.compile(videlit, re.IGNORECASE)


def song_text(text: str = None, chords: bool = False) -> str | None:
    if not text:
        return None
    text = text.split("\n")
    text = text if chords else [i for i in text if not is_chord_line(i)]
    for i, t in enumerate(text):
        if videlit_pattern.search(t.lower()):
            text[i] = f"\n<b>{t}</b>"
    return html.unescape("\n".join(text))


def is_chord_line(line: str):
    tokens = re.sub(r"\s+", " ", line).strip().split(" ")
    allowed_tokens = {"|", "/", "(", ")", "-", "x2", "x3", "x4", "x5", "x6", "•", "NC"}
    for i in tokens:
        if i.strip() and not chord_pattern.match(i) and all(j not in i for j in allowed_tokens):
            return False
    return True
