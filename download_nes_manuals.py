#!/usr/bin/env python3
"""
Download NES Spanish instruction manuals from MediaFire links.
This script includes rate limiting to be respectful to MediaFire's servers.
"""

import os
import re
import time
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


# Configuration
DOWNLOAD_DIR = Path("./manuals")
DELAY_BETWEEN_DOWNLOADS = 3  # seconds between each download
REQUEST_TIMEOUT = 30  # seconds
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
TEST_MODE = False  # Set to False to download all manuals
MAX_TEST_DOWNLOADS = 1  # Number of manuals to download in test mode


# MediaFire links extracted from the webpage
MEDIAFIRE_LINKS = {
    # Games
    "A Boy and his Blob": "http://www.mediafire.com/?pyjx3apy79x5932",
    "Addams Family": "http://www.mediafire.com/?p9gasq8j3prk3ws",
    "Adventure Island Classic": "http://www.mediafire.com/?n34j1ihvd31u600",
    "Adventure Island Part II": "http://www.mediafire.com/?ev22k9a284vb5r3",
    "Adventures in the Magic Kingdom": "http://www.mediafire.com/?d56dd5g9crdf3c6",
    "Adventures of Bayou Billy": "http://www.mediafire.com/?w0yo99t8o2dv8v3",
    "Adventures of Lolo": "http://www.mediafire.com/?czo2o882gr4cr1q",
    "Adventures of Lolo 2": "http://www.mediafire.com/?znmidmujklm0ywo",
    "Adventures of Lolo 3": "http://www.mediafire.com/?pa8l2qcv8rr22pl",
    "Air Fortress": "http://www.mediafire.com/?4jv0getb7b74kbk",
    "Airwolf": "http://www.mediafire.com/?jr243j5l2s4fstt",
    "Alpha Mission": "http://www.mediafire.com/?68ax6202gli3w76",
    "Arch Rivals": "http://www.mediafire.com/?gr6590oj59tcikq",
    "Asterix": "http://www.mediafire.com/?jtovpz21crktyc5",
    "Astyanax": "http://www.mediafire.com/?uq282svp8xmeb1o",
    "Athletic World": "http://www.mediafire.com/?ctv19hpgwayx43q",
    "Bad Dudes vs Dragonninja": "http://www.mediafire.com/?zk9zhhon0rq07ns",
    "Balloon Fight": "http://www.mediafire.com/?dp5s4e3pu85q0jd",
    "Barker Bills Trick Shooting": "http://www.mediafire.com/?957uown0yem0srn",
    "Baseball": "http://www.mediafire.com/?gvb4ddf62dhq6qu",
    "Batman Return of the Joker": "http://www.mediafire.com/?jij39hl7cu47rur",
    "Batman The Video Game": "http://www.mediafire.com/?5xybdtpk3ck1ghf",
    "Battle of Olympus": "http://www.mediafire.com/?7i1dgw915u01638",
    "Battletoads": "http://www.mediafire.com/?664716uc1m8wanb",
    "Best of the Best": "http://www.mediafire.com/?sdo0mi2svghux3v",
    "Bigfoot": "http://www.mediafire.com/?h7jr4nyc20fuae0",
    "Bionic Commando": "http://www.mediafire.com/?gb1g0i9fk7op25q",
    "Blades of Steel": "http://www.mediafire.com/?5afwc69ua2mb79g",
    "Blaster Master": "http://www.mediafire.com/?4wuosv2nhw14qfj",
    "Blue Shadow": "http://www.mediafire.com/?jnreo5i8ctck5oj",
    "Blues Brothers": "http://www.mediafire.com/?tzfz8934lh4bov7",
    "Boulder Dash": "http://www.mediafire.com/?whmck4wwwwujp36",
    "Bubble Bobble": "http://www.mediafire.com/?t4h9mdmmm93k87k",
    "Bugs Bunny Blowout": "http://www.mediafire.com/?poyvve26dv7a6pm",
    "Burai Fighter": "http://www.mediafire.com/?dgox5ogtgaprzak",
    "California Games": "http://www.mediafire.com/?tr0ybigcpv3g9sp",
    "Captain Planet": "http://www.mediafire.com/?p7200offc3a59i0",
    "Captain Skyhawk": "http://www.mediafire.com/?tbx3358rga6tbzk",
    "Castelian": "http://www.mediafire.com/?487ox1wa7pwyxa1",
    "Castlevania": "http://www.mediafire.com/?85e3kz0zut4bagz",
    "Castlevania II": "http://www.mediafire.com/?loi85oz4e52ut0m",
    "Championship Rally": "http://www.mediafire.com/?he4xqfyiq3iccel",
    "Chessmaster": "http://www.mediafire.com/?7r5c0u51u4puagz",
    "Chip n Dale Rescue Rangers": "http://www.mediafire.com/?bbw96grqa183rue",
    "Chip n Dale Rescue Rangers 2": "https://www.mediafire.com/file/hj9a7sl0ampqcbg",
    "City Connection": "http://www.mediafire.com/?zmyqp6zmj9mz6sk",
    "Cobra Triangle": "http://www.mediafire.com/?f61v3zb5cdztfpj",
    "Corvette ZR-1": "http://www.mediafire.com/?s0227b2wfnoev4s",
    "Crackout": "http://www.mediafire.com/?zdw4z2gnyprlout",
    "Darkman": "http://www.mediafire.com/?qafllgvdzxukva0",
    "Days of Thunder": "http://www.mediafire.com/?heeac3u2fkq5ree",
    "Die Hard": "http://www.mediafire.com/?vyzghl5e80zfgp1",
    "Digger T Rock": "http://www.mediafire.com/?pc41k4l94k88aup",
    "Donkey Kong 3": "http://www.mediafire.com/?7y0u75oe55ywv42",
    "Donkey Kong Classics": "http://www.mediafire.com/?u6dt7utb8bfp2t0",
    "Donkey Kong Jr": "http://www.mediafire.com/?ahifcyljz75jotu",
    "Donkey Kong Jr Math": "http://www.mediafire.com/?ie5h34r0xb037f6",
    "Double Dragon": "http://www.mediafire.com/?uzh11op2q3fx2z2",
    "Double Dragon II": "http://www.mediafire.com/?5zc5819z1frrw51",
    "Double Dragon III": "http://www.mediafire.com/?ylc36drrno1vsk6",
    "Double Dribble": "http://www.mediafire.com/?2v5oyg2zoz4v3fq",
    "Dr Mario": "http://www.mediafire.com/?ufqxhhe9j8q15qb",
    "Dragon Ball": "http://www.mediafire.com/?o38rw3edrwnbmnc",
    "Dragons Lair": "http://www.mediafire.com/?1vqk1qn1ez7a8zs",
    "Duck Hunt": "http://www.mediafire.com/?bva551ywyfvu570",
    "Duck Tales": "http://www.mediafire.com/?ol9hh98q4269xlw",
    "Duck Tales 2": "https://www.mediafire.com/?xok850bd9aps22h",
    "Dynablaster": "http://www.mediafire.com/?s28caa3zzavhppc",
    "Elite": "http://www.mediafire.com/?amchfoakku6uoqb",
    "Excitebike": "http://www.mediafire.com/?f2ub2l1vsa0hhb4",
    "Faxanadu": "http://www.mediafire.com/?snvbm0x4bf40s0p",
    "Festers Quest": "http://www.mediafire.com/?mldpa8j4fld4x9q",
    "Fighting Golf": "http://www.mediafire.com/?2u0iguck1iu1biq",
    "Flintstones": "http://www.mediafire.com/?n6b8qn7122s0jcf",
    "Four Players Tennis": "http://www.mediafire.com/?h4nq7y63w04029x",
    "Galaga": "http://www.mediafire.com/?ypn898cv44wmfs9",
    "Galaxy 5000": "http://www.mediafire.com/?e8pizycx8zz68ag",
    "Gauntlet II": "http://www.mediafire.com/?ogbrwz147lzq5lg",
    "George Foremans KO Boxing": "http://www.mediafire.com/?zgtq8tdmpsgxvgr",
    "Ghost n Goblins": "http://www.mediafire.com/?4sx8n34ff5l8ca8",
    "Ghostbusters II": "http://www.mediafire.com/?p7khrpk7pcxxfjc",
    "Goal": "http://www.mediafire.com/?1kcflq91grhsmrq",
    "Goal 2": "http://www.mediafire.com/?2uqrbhq4rwhi1rw",
    "Godzilla": "http://www.mediafire.com/?5g7jblon8dh9ld9",
    "Golf": "http://www.mediafire.com/?5s4sgba2c5j7r2p",
    "Goonies II": "http://www.mediafire.com/?h91wftk3yka3iyn",
    "Gradius": "http://www.mediafire.com/?n0695gi3qe5n3fc",
    "Gremlins 2": "http://www.mediafire.com/?dy4akpmp6aljdtm",
    "Guardian Legend": "http://www.mediafire.com/?pbkdh2i42b9brbc",
    "Guerrilla War": "http://www.mediafire.com/?w99nel11mhmfvfr",
    "Gumshoe": "http://www.mediafire.com/?tn04i968xlzy36q",
    "Gun Smoke": "http://www.mediafire.com/?l6au2bt5zch37fx",
    "Hammerin Harry": "http://www.mediafire.com/?mhnfms00ywvsasq",
    "High Speed": "http://www.mediafire.com/?k5vq5l4kb1ud86j",
    "Hogans Alley": "http://www.mediafire.com/?u5bttr24g5tia4j",
    "Hook": "http://www.mediafire.com/?8rap42olfsb2nrc",
    "Hoops": "http://www.mediafire.com/?o8q4j2rzmc0821b",
    "Hudson Hawk": "http://www.mediafire.com/?vw5bh8xzrhyyxh5",
    "Hunt for Red October": "http://www.mediafire.com/?6bmjlpg9gj4yenh",
    "Ice Climber": "http://www.mediafire.com/?wl36zqcuw0fcr53",
    "Ice Hockey": "http://www.mediafire.com/?5yljlxsztr65f4c",
    "Ikari Warriors": "http://www.mediafire.com/?fuwvqfbo8b8hkb7",
    "Incredible Crash Dummies": "http://www.mediafire.com/?bgaeqcvy2glg6s9",
    "Indiana Jones Last Crusade": "http://www.mediafire.com/?6dgrakfpdp52t0o",
    "Indy Heat": "http://www.mediafire.com/?aipcy3q0ri3eqy4",
    "Iron Tank": "http://www.mediafire.com/?hwz8rmycd2cahat",
    "Isolated Warrior": "http://www.mediafire.com/?6nraplchq3ce109",
    "Ivan Stewarts Super Off Road": "http://www.mediafire.com/?mcdghyvbajrvqro",
    "Jack Nicklaus Greatest 18 Holes": "http://www.mediafire.com/?z5l5ac6p95p8cv4",
    "Jackie Chans Action Kung Fu": "http://www.mediafire.com/?i9uedt359y5espq",
    "Jetsons": "http://www.mediafire.com/?u97o3vg1r4g1u1t",
    "Jimmy Connors Tennis": "http://www.mediafire.com/?kuh1uflee5q4743",
    "Joe and Mac": "http://www.mediafire.com/?5f2b9rr1pi841c0",
    "Journey to Silius": "http://www.mediafire.com/?gcm4ipztcqg9p9m",
    "Jungle Book": "http://www.mediafire.com/?hl20ihy5j55t35u",
    "Kabuki Quantum Fighter": "http://www.mediafire.com/file/q90c6b4ldgy85he",
    "Kick Off": "http://www.mediafire.com/?aka1mri4c4j1hu0",
    "Kickle Cubicle": "http://www.mediafire.com/?wyq45s9k12ss5n6",
    "Kid Icarus": "http://www.mediafire.com/?3psv2cvaqh6gfcm",
    "Kirbys Adventure": "http://www.mediafire.com/?9v3nf5x31k38h7m",
    "Knight Rider": "http://www.mediafire.com/?65a3dv5xw8cvdzl",
    "Konami Hyper Soccer": "http://www.mediafire.com/?6ewb4m7ivt9n9xp",
    "Kung Fu": "http://www.mediafire.com/?2kmsnjbishvq2ig",
    "Legend of Prince Valiant": "http://www.mediafire.com/?5r6nflxafamadm8",
    "Legend of Zelda": "http://www.mediafire.com/?8jae7totg2k0o5w",
    "Lemmings": "http://www.mediafire.com/?xo883j68r8yfud5",
    "Life Force": "http://www.mediafire.com/?a37dx8chq112lse",
    "Little Nemo": "http://www.mediafire.com/?02rvobo9cxdedhy",
    "Little Samson": "http://www.mediafire.com/?bh2agk7bflztzdv",
    "Low G Man": "http://www.mediafire.com/?jibhgzaj6szrgmg",
    "Lunar Pool": "http://www.mediafire.com/?dx5s8c0nxbt1221",
    "Mach Rider": "http://www.mediafire.com/?c2zc8665xudvwlk",
    "Maniac Mansion": "http://www.mediafire.com/?29aq9xr8vdrrnan",
    "Marble Madness": "http://www.mediafire.com/?5g1913amlg4nzwu",
    "Mario and Yoshi": "http://www.mediafire.com/?rgba2138shr2s0r",
    "Mario Bros": "http://www.mediafire.com/?dzt25hqsw6z2v18",
    "McDonaldland": "http://www.mediafire.com/?veez25fnhszzlwd",
    "Mega Man": "http://www.mediafire.com/?8nkcfo1uaxldbt5",
    "Mega Man 2": "http://www.mediafire.com/?rbi54w0c7frcj0g",
    "Mega Man 3": "http://www.mediafire.com/?a9dt3mksqfxzsr2",
    "Mega Man 4": "http://www.mediafire.com/?4xspkilojjs32sd",
    "Mega Man 5": "http://www.mediafire.com/?r6zw365yzd2zph7",
    "Metal Gear": "http://www.mediafire.com/?7ag2hrgurufkr9z",
    "Metroid": "http://www.mediafire.com/?q6ps2cd3tpo9dic",
    "Mighty Bombjack": "http://www.mediafire.com/?sb2s2aw59hx4e4a",
    "Mike Tysons Punch-Out": "http://www.mediafire.com/?2st57nrqbkpi4b9",
    "Mission Impossible": "http://www.mediafire.com/?2m5di7id6m410z4",
    "NES Open Tournament Golf": "http://www.mediafire.com/?6aed64utbb91338",
    "New Ghostbusters II": "http://www.mediafire.com/?f4fxlv2qz47qgbc",
    "Newzealand Story": "http://www.mediafire.com/?inl195b81lqc8hc",
    "Nintendo World Cup": "http://www.mediafire.com/?8p9latr2us2w1a1",
    "North and South": "http://www.mediafire.com/?a7kccimrw9bsdpc",
    "Operation Wolf": "http://www.mediafire.com/?rcfhfp58c6fwfo5",
    "POW": "http://www.mediafire.com/?8ci95tfn5q5xi1i",
    "Panic Restaurant": "http://www.mediafire.com/?s01ksc04x3zdl96",
    "Paperboy": "http://www.mediafire.com/?q9uwc5hp0w806ay",
    "Paperboy 2": "http://www.mediafire.com/?70fw2adc7ppbbf9",
    "Parasol Stars": "http://www.mediafire.com/?agpmmyvptoio1xf",
    "Phantom Air Mission": "http://www.mediafire.com/?nddhbrbi1jssnc4",
    "Pin-Bot": "http://www.mediafire.com/?w9imuq3yi6w8y8y",
    "Pinball": "http://www.mediafire.com/?zia35rpagti1w1z",
    "Popeye": "http://www.mediafire.com/?b1zdrvzscdh5fz0",
    "Power Blade": "http://www.mediafire.com/?vb4e1902auxfrx9",
    "Prince of Persia": "http://www.mediafire.com/?3q0xw9le3wxvwbv",
    "Pro Wrestling": "http://www.mediafire.com/?eygo4cffv7vaaar",
    "Probotector": "http://www.mediafire.com/?gyptjcfnfib74ww",
    "Punch-Out": "http://www.mediafire.com/?wdx885cgve3mqw0",
    "Puzznic": "http://www.mediafire.com/?iygu8dwce79ddu3",
    "RC Pro-Am": "http://www.mediafire.com/?bkud7rlrd25712j",
    "Racket Attack": "http://www.mediafire.com/?ch125wm5pca99m9",
    "Rad Gravity": "http://www.mediafire.com/?0igggtwkx9a07u3",
    "Rad Racer": "http://www.mediafire.com/?228dw8rlkfkb8c8",
    "Rad Racer (Folleto)": "http://www.mediafire.com/?ad55fesnl7yas8k",
    "Rainbow Islands": "http://www.mediafire.com/?54s5i5anw5a5pqi",
    "Rescue Embassy Mission": "http://www.mediafire.com/?qzsvq74dl9979q4",
    "Road Fighter": "http://www.mediafire.com/?sb4rf9jtrr155cc",
    "RoadBlasters": "http://www.mediafire.com/?bceaq11pdvogng5",
    "Robin Hood": "http://www.mediafire.com/?9pkba3amnyo0x2h",
    "RoboCop": "http://www.mediafire.com/?v0egv573qvp155w",
    "RoboCop 2": "http://www.mediafire.com/?ao9tt870kt9wlw4",
    "RoboCop 3": "http://www.mediafire.com/?7qje00zx46397w7",
    "RoboWarrior": "http://www.mediafire.com/?gbsucqjycurh7r5",
    "Rockin Kats": "http://www.mediafire.com/?axt392nm564s85t",
    "Rodland": "http://www.mediafire.com/?pxeztwsqf04xq08",
    "Rollergames": "http://www.mediafire.com/?nq9nf08p38bz1y2",
    "Rushn Attack": "http://www.mediafire.com/?4ygi0r30ah1l6kl",
    "Rygar": "http://www.mediafire.com/?pvuqp7jqie2ka6i",
    "Section-Z": "http://www.mediafire.com/?ymz7lg2d1vvsnh9",
    "Shadow Warriors": "http://www.mediafire.com/?22v4gdpu08c5ar7",
    "Shadow Warriors II": "http://www.mediafire.com/?r79ba3d8cm1ev5o",
    "Shatterhand": "http://www.mediafire.com/?vflepppn59jeyl7",
    "Silent Service": "http://www.mediafire.com/?0i01xdikvkn6n7e",
    "Simpsons Bart vs Space Mutants": "http://www.mediafire.com/?vyj6yixgry41cf8",
    "Simpsons Bart vs The World": "http://www.mediafire.com/?taj6t2sgsg6mmgw",
    "Skate or Die": "http://www.mediafire.com/?7th6ykhjlu8m77s",
    "Ski or Die": "http://www.mediafire.com/?udmn5w0soejraut",
    "Smash TV": "http://www.mediafire.com/?76ou9j5bqktoyqe",
    "Smurfs": "http://www.mediafire.com/?cddoejgdkv78box",
    "Snake Rattle n Roll": "http://www.mediafire.com/?iqle0fcnkudpkqq",
    "Snakes Revenge": "http://www.mediafire.com/?i1cece08p46p0fv",
    "Snow Brothers": "http://www.mediafire.com/?wxyg8y9k5coo157",
    "Snowboard Challenge": "http://www.mediafire.com/?giguglg2io153cb",
    "Soccer": "http://www.mediafire.com/?r9k63hd595f6f0j",
    "Solar Jetman": "http://www.mediafire.com/?6qnoxv6ajsdgb96",
    "Solomons Key": "http://www.mediafire.com/?3yjepcsk9ygxo1y",
    "Solomons Key 2": "http://www.mediafire.com/?e17657nnyrcvhy0",
    "Solstice": "http://www.mediafire.com/?756l7u2pocu8hjo",
    "Spider-Man Return of Sinister Six": "http://www.mediafire.com/?6ai96giyntvp1zl",
    "Star Force": "http://www.mediafire.com/?mwsr4l7ofk1aoa1",
    "Star Wars": "http://www.mediafire.com/?220wi67teyyy3z8",
    "Star Wars Empire Strikes Back": "http://www.mediafire.com/?b99xuu6hxdaft7u",
    "StarTropics": "http://www.mediafire.com/?oxxwon8yf5n3zi2",
    "Stealth ATF": "http://www.mediafire.com/?n84qr4k80k6f3s1",
    "Street Gangs": "http://www.mediafire.com/?pk0deqxhdmz80q5",
    "Super Mario Bros": "http://www.mediafire.com/?3b88z8gkkt2c0dy",
    "Super Mario Bros and Duck Hunt": "http://www.mediafire.com/?1h3v7qgk86d7k2u",
    "Super Mario Bros and Tetris and Nintendo World Cup": "http://www.mediafire.com/?4pxw0smw8pxpqm9",
    "Super Mario Bros 2": "http://www.mediafire.com/?mbms1m4quib51vc",
    "Super Mario Bros 3": "http://www.mediafire.com/?9rgbnclz3aeoq0v",
    "Super Spike VBall": "http://www.mediafire.com/?3c3xg2171snm80z",
    "Super Spy Hunter": "http://www.mediafire.com/?huetaa8w89e9tsx",
    "Super Turrican": "http://www.mediafire.com/?ey5youn594cl94m",
    "Sword Master": "http://www.mediafire.com/?d8p9eb5881rdrno",
    "Tale Spin": "http://www.mediafire.com/?k3ucaoje36zxh75",
    "Tecmo Cup Football": "http://www.mediafire.com/?1ivilk2i2pu50ov",
    "Tecmo World Cup Soccer": "http://www.mediafire.com/?r6ur81is3dp2h1w",
    "Tecmo World Wrestling": "http://www.mediafire.com/?919kbzu0mmabvcu",
    "Teenage Mutant Hero Turtles": "http://www.mediafire.com/?3bmapah50o1p7vv",
    "Teenage Mutant Hero Turtles II": "http://www.mediafire.com/?9i3mw2rlbfjwfil",
    "Teenage Mutant Hero Turtles Tournament Fighters": "https://www.mediafire.com/?j18lfrvvct4i56j",
    "Tennis": "http://www.mediafire.com/?qs263wpmay9t40w",
    "Terminator 2": "http://www.mediafire.com/?jjdy20p75aoplgv",
    "Tetris": "http://www.mediafire.com/?thrn5cyfpo1f7db",
    "Tetris 2": "http://www.mediafire.com/?0v5enw1s24lvx55",
    "Tiger-Heli": "http://www.mediafire.com/?od1u7ozxt5a9rlk",
    "Time Lord": "http://www.mediafire.com/?947em70nksluga7",
    "Tiny Toon Adventures 2": "http://www.mediafire.com/?aztfy5f1rzjb812",
    "To the Earth": "http://www.mediafire.com/?xspqvni53mn07w7",
    "Tom and Jerry": "http://www.mediafire.com/?dnt9cl9a20i76jl",
    "Top Gun": "http://www.mediafire.com/?rryk61hytylx8hk",
    "Top Gun Second Mission": "http://www.mediafire.com/?c4e69clafjzkofh",
    "Total Recall": "http://www.mediafire.com/?0kx6f7unkpci3uc",
    "Totally Rad": "http://www.mediafire.com/?is8m1x7arhnsvr8",
    "Track and Field II": "http://www.mediafire.com/?lxafo5pbwdbrb71",
    "Track and Field in Barcelona": "http://www.mediafire.com/?2ar305r3wtqxjja",
    "Trog": "http://www.mediafire.com/?l0cxq7lqu7um98v",
    "Trojan": "http://www.mediafire.com/?x6igfxa65kw8de6",
    "Turbo Racing": "http://www.mediafire.com/?awmyaj7h9m4zi9n",
    "Ufouria": "http://www.mediafire.com/?kyxuaay8rz1ye5t",
    "Ultimate Air Combat": "http://www.mediafire.com/?m8agt2tievwuqpf",
    "Ultimate Stuntman": "http://www.mediafire.com/?3yn6bc8b990d5n4",
    "Warios Woods": "http://www.mediafire.com/?ak2187udlbc3i87",
    "Werewolf": "http://www.mediafire.com/?qz2am24iweq04kg",
    "Wild Gunman": "http://www.mediafire.com/?yst6f6els1c6qlu",
    "Willow": "http://www.mediafire.com/?xuav1yasl5mmsm5",
    "Wizards and Warriors": "https://www.mediafire.com/?ap9ezpjxawylfhv",
    "Wizards and Warriors II": "http://www.mediafire.com/?076ym847ztzzj45",
    "Wizards and Warriors III": "http://www.mediafire.com/?hegb7wc6ycw783b",
    "World Champ": "http://www.mediafire.com/?qeqcnnn0id21778",
    "Wrath of Black Manta": "http://www.mediafire.com/?1j3s5g6xlvxmqg4",
    "Wrecking Crew": "http://www.mediafire.com/?dnr50d46u0m7kj7",
    "WWF King of the Ring": "http://www.mediafire.com/?rvalnuqew18q46r",
    "WWF Wrestlemania": "http://www.mediafire.com/?2ys6ua5s7d66u9t",
    "WWF Wrestlemania Challenge": "http://www.mediafire.com/?kn9gsco32f7n2om",
    "WWF Wrestlemania Steel Cage": "http://www.mediafire.com/?gl0w20ibz1r1cgg",
    "Xevious": "http://www.mediafire.com/?6gt47fz12xi9tm3",
    "Zelda II": "http://www.mediafire.com/?v33ze3cbdt82z87",

    # Hardware
    "Hardware - Cleaning Kit": "http://www.mediafire.com/?k8n0h0y507lbr0y",
    "Hardware - Control Deck": "http://www.mediafire.com/?moek54tste122bu",
    "Hardware - Configuracion Antena": "http://www.mediafire.com/?9hckcl5vrk55r8y",
    "Hardware - Game Genie (Precauciones)": "http://www.mediafire.com/?z3kjbvo99axtcqs",
    "Hardware - Game Genie": "http://www.mediafire.com/?w3y28db8agmv08g",
    "Hardware - Laser Scope": "http://www.mediafire.com/?p2lyea25r5h4y9f",
    "Hardware - NES Advantage": "http://www.mediafire.com/?9yzxv2n6gz15quv",
    "Hardware - NES Four Score": "http://www.mediafire.com/?w67dxjb6w8j2dxk",
    "Hardware - NES MAX": "http://www.mediafire.com/?8s4mup1za908ac4",
    "Hardware - Wireless-InfraRed": "http://www.mediafire.com/?v7x9wf9t4pbbbbb",
    "Hardware - Zapper": "http://www.mediafire.com/?x7ev5gnpx930a79",

    # Advertising
    "Publicidad - Ficha Club Nintendo": "http://www.mediafire.com/?c75bjgvazc9bdk5",
    "Publicidad - Publicidad Konami": "http://www.mediafire.com/?cyci7kst33q6q88",
    "Publicidad - Publicidad Nintendo": "http://www.mediafire.com/?wpygnm88lep9she",
}


def sanitize_filename(name):
    """Convert name to a safe filename in lowercase with hyphens."""
    # Convert to lowercase
    name = name.lower()
    # Remove or replace unsafe characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Replace spaces and other separators with hyphens
    name = re.sub(r'[\s&\']+', '-', name)
    # Remove multiple consecutive hyphens
    name = re.sub(r'-+', '-', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    return name


def get_direct_download_url(mediafire_url):
    """
    Parse MediaFire page to get the direct download link.
    MediaFire shows a page first, then you need to extract the actual file URL.
    """
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(mediafire_url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for the download button/link
        # MediaFire uses different selectors, trying multiple approaches
        download_link = None

        # Method 1: Look for download button with specific ID
        download_btn = soup.find('a', {'id': 'downloadButton'})
        if download_btn and download_btn.get('href'):
            download_link = download_btn['href']

        # Method 2: Look for links with download class
        if not download_link:
            download_btn = soup.find('a', class_=lambda x: x and 'download' in x.lower())
            if download_btn and download_btn.get('href'):
                download_link = download_btn['href']

        # Method 3: Look for direct file link in page
        if not download_link:
            # Sometimes the direct link is in a specific div
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'download' in href and href.startswith('http'):
                    download_link = href
                    break

        return download_link

    except Exception as e:
        print(f"Error getting download URL: {e}")
        return None


def download_file(url, name, output_dir):
    """Download a single file from MediaFire."""
    try:
        print(f"Processing: {name}")

        # Get the direct download URL
        direct_url = get_direct_download_url(url)

        if not direct_url:
            print(f"  ❌ Could not find download link for {name}")
            return False

        # Download the file
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(direct_url, headers=headers, timeout=REQUEST_TIMEOUT, stream=True)
        response.raise_for_status()

        # Always use our sanitized filename format
        filename = f"{sanitize_filename(name)}.pdf"
        filepath = output_dir / filename

        # Check if file already exists
        if filepath.exists():
            print(f"  ⏭️  Already downloaded: {filename}")
            return True

        # Download with progress
        total_size = int(response.headers.get('content-length', 0))
        with open(filepath, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"  📥 {progress:.1f}%", end='\r')

        print(f"  ✅ Downloaded: {filename}")
        return True

    except Exception as e:
        print(f"  ❌ Error downloading {name}: {e}")
        return False


def main():
    """Main download function."""
    # Create download directory
    DOWNLOAD_DIR.mkdir(exist_ok=True)

    # Determine how many to download
    items_to_download = list(MEDIAFIRE_LINKS.items())
    if TEST_MODE:
        items_to_download = items_to_download[:MAX_TEST_DOWNLOADS]

    print(f"NES Spanish Manuals Downloader")
    print(f"=" * 50)
    if TEST_MODE:
        print(f"🧪 TEST MODE: Downloading {len(items_to_download)} manual(s)")
    print(f"Total manuals to download: {len(items_to_download)}")
    print(f"Output directory: {DOWNLOAD_DIR.absolute()}")
    print(f"Delay between downloads: {DELAY_BETWEEN_DOWNLOADS} seconds")
    print(f"=" * 50)
    print()

    successful = 0
    failed = 0
    skipped = 0

    for idx, (name, url) in enumerate(items_to_download, 1):
        print(f"[{idx}/{len(MEDIAFIRE_LINKS)}] ", end='')

        result = download_file(url, name, DOWNLOAD_DIR)

        if result:
            successful += 1
        else:
            failed += 1

        # Rate limiting - wait between downloads
        if idx < len(items_to_download):
            print(f"  ⏳ Waiting {DELAY_BETWEEN_DOWNLOADS} seconds...")
            time.sleep(DELAY_BETWEEN_DOWNLOADS)

        print()

    # Summary
    print()
    print("=" * 50)
    print(f"Download Summary:")
    print(f"  ✅ Successful: {successful}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📂 Files in {DOWNLOAD_DIR.absolute()}")
    print("=" * 50)


if __name__ == "__main__":
    main()
