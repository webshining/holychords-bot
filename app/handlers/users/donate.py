from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery

from app.keyboards import get_donate_markup
from loader import dp, _


@dp.message(Command("donate"))
async def donate_handler(message: Message, command):
    amount = 10
    if command.args and command.args.isnumeric():
        amount = int(command.args)
    prices = [LabeledPrice(label="XTR", amount=amount)]
    await message.answer_invoice(title=_("Support the Project"),
                                 description=_(
                                     "If you enjoy using this bot, please consider making a small donation to support its development.\n"
                                     "You can also specify a different donation amount by sending /donate followed by the amount, for example: /donate 17"
                                 ),
                                 prices=prices,
                                 provider_token="",
                                 payload="donate",
                                 currency="XTR",
                                 reply_markup=get_donate_markup(amount))


@dp.pre_checkout_query()
async def donate_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(True)


@dp.message(F.successful_payment)
async def donate_process_handler(message: Message):
    print(message.successful_payment)
    await message.answer(_("🎉 Thank you for your donation\nYour support helps keep this project alive ❤️"))
