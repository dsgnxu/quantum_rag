# Примеры диалогов RAG-бота (Задание 4)

## Успешные ответы

### Вы
Кто такой Xarn Velgor?

### Бот
1. Сначала найду фрагменты по запросу: «Кто такой Xarn Velgor?».
2. В документе `knowledge_base/xarn_velgor.md` (score=0.627) есть релевантный текст.
3. Следовательно, опираюсь на CONTEXT.

Итоговый ответ: Xarn Velgor — Void Sovereign Dominion Sphere и правая рука Overlord Krynn. Ранее известен как Aric Orin, Flux Guardians Knight из Sandveil. После падения на Emberfall получил кибернетический костюм и титул Xarn Velgor. Владеет красным fluxblade и использует void tide of Synth Flux. Командует флотом Void Cruiser и штурмовыми подразделениями Null Sentinel. Его дети — Kael Orin и Seren Vahl — стали ключевыми фигурами Free Concord.

*Источники:* knowledge_base/xarn_velgor.md, knowledge_base/master_thalos.md, knowledge_base/emberfall.md, knowledge_base/grothak.md

### Вы
Что такое Void Core?

### Бот
1. Сначала найду фрагменты по запросу: «Что такое Void Core?».
2. В документе `knowledge_base/void_core.md` (score=0.706) есть релевантный текст.
3. Следовательно, опираюсь на CONTEXT.

Итоговый ответ: Void Core — боевая станция Dominion Sphere, способная уничтожить планету одним выстрелом. Оснащена суперлазером и защищена флотом Void Cruiser и Shade Dart. Планы станции были украдены Free Concord при участии Seren Vahl. Kael Orin уничтожил первую Void Core, попав в реактор через Synth Flux. Позже Dominion Sphere строила вторую станцию над Verdance.

*Источники:* knowledge_base/void_core.md, knowledge_base/void_cruiser.md, knowledge_base/void_tide.md, knowledge_base/verdance.md

### Вы
Кто пилотирует Nebula Runner?

### Бот
1. Сначала найду фрагменты по запросу: «Кто пилотирует Nebula Runner?».
2. В документе `knowledge_base/nebula_runner.md` (score=0.724) есть релевантный текст.
3. Следовательно, опираюсь на CONTEXT.

Итоговый ответ: Nebula Runner — лёгкий грузовой корабль, знаменитый скоростью в hyperrelay. Пилотируется Jorik Vane и Grothak, оснащён скрытыми оружейными системами. Участвовал в эвакуации с Frostspire и атаке на Void Core. Считается одним из быстрейших гражданских кораблей внешних миров. Для Free Concord Falcon стал символом удачи и дерзости.

*Источники:* knowledge_base/nebula_runner.md, knowledge_base/jorik_vane.md, knowledge_base/grothak.md, knowledge_base/xarn_velgor.md

### Вы
Где Elder Myrr обучал Kael Orin?

### Бот
1. Сначала найду фрагменты по запросу: «Где Elder Myrr обучал Kael Orin?».
2. В документе `knowledge_base/kael_orin.md` (score=0.628) есть релевантный текст.
3. Следовательно, опираюсь на CONTEXT.

Итоговый ответ: Kael Orin вырос на Sandveil у дяди и тёти, не зная о своём происхождении. После встречи с Flux Elder Thalos узнал о Synth Flux и получил fluxblade отца. Присоединился к Free Concord вместе с Jorik Vane, Grothak, Unit Pex-7 и Protocol Unit Vox. Уничтожил Void Core с помощью Synth Flux во время битвы при Явине. Позже обучался у Elder Myrr на Mistgrove и противостоял Xarn Velgor. Цель Kael Orin — восстановить Flux Guardians Order после падения Dominion Sphere.

*Источники:* knowledge_base/kael_orin.md, knowledge_base/elder_myrr.md, knowledge_base/mistgrove.md, knowledge_base/master_thalos.md

### Вы
Что такое Synth Flux?

### Бот
1. Сначала найду фрагменты по запросу: «Что такое Synth Flux?».
2. В документе `knowledge_base/synth_flux.md` (score=0.723) есть релевантный текст.
3. Следовательно, опираюсь на CONTEXT.

Итоговый ответ: Synth Flux — энергетическое поле, связывающее всё живое в галактике. Flux Guardians используют flux dawn для защиты и гармонии. Void Dominion черпают силу из void tide через страх и гнев. Способности включают телекинез, предвидение и усиление тела. В древних текстах упоминаются flux motes как посредники связи с Synth Flux.

*Источники:* knowledge_base/synth_flux.md, knowledge_base/fluxblade.md, knowledge_base/elder_myrr.md, knowledge_base/void_tide.md

## Случаи «Я не знаю»

### Вы
Какой сейчас курс доллара в банке QuantumForge?

### Бот
1. Ищу информацию в векторном индексе.
2. Релевантных фрагментов нет.
3. Итоговый ответ: Я не знаю.

### Вы
Кто командовал флотом Shadow Orchid?

### Бот
1. Ищу информацию в векторном индексе.
2. Релевантных фрагментов нет.
3. Итоговый ответ: Я не знаю.
