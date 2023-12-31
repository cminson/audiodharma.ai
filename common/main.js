/*
 *
 * if (query.length < MIN_HUMAN_INPUT_LENGTH) return
 * main.js - javascript for audiodharma.ai
 * author:  christopher minson
 *
 */
const URL_BASE = "https://www.audiodharma.ai/";
const DEV_URL_BASE = "https://www.audiodharma.ai/index.html";
const SERVER_ADDRESS = "https://www.audiodharma.ai:3022";
const URL_INDEX_PAGE = URL_BASE + "index.html?";
const PATH_SUMMARIES =  "../data/summaries/";
const PATH_TEXT =  "../data/text/";
const BASE_URL_MP3 = "https://audiodharma.us-east-1.linodeobjects.com/";

const PATH_BUSY_ICON = './resources/images/tao100.png';
const INC_ROTATION_ANGLE = 10;
const MIN_HUMAN_INPUT_LENGTH = 3;

const ERROR_SERVICE_OFFLINE = "All is transient.<p>Sophia is currently updating.<br>Please try again later."

const INTRO_CHAT_DIALOG = "Sophia is an AI trained in Buddhist philosophy, through her study of over 12,000 Dharma talks given by hundreds of teachers. Ask her anything on this topic. She will respond with her personal views, and then provide links to the talks that most informed her opinions. See the Guide for more details.";

var Busy = false;
var ChatHistory = "";
var DictTalkExclusions = {};
var ListDisplayedTalks = [];
var CurrentTitle = "";


function displayHome() {

    window.open("index.html", "_self");
}

function displayGuide() {

    window.open("guide.html", "_self");
}

function afterTransition() {
    window.location.replace(DEV_URL_BASE);

}


function slideUp() {

    document.querySelector('.gateway').classList.add('slide-out');
    div.classList.add('slide-out');
}


function login() {

    console.log("login");
    code =  $("#ID_LOGIN_INPUT").val();

    if (code.toLowerCase() == 'imc') {
    //if (true) {

        div = document.getElementById("ID_GATEWAY");
        div.addEventListener('transitionend', afterTransition);
        slideUp();
    }

}

function initGuide() {

    CurrentTitle = "Guide"
}

function initIndex() {

    Busy = false;
    ListDisplayedTalks = [];

    initBusyIcon();

    var queryString = window.location.search;
    var params = new URLSearchParams(queryString);
    var command = params.get('c');
    var query = params.get('q');

    console.log('init queryString: ' + queryString)
    console.log('init command: ' + command)

    switch (command) {
        case 'GET_ALL_TALKS':
            getAllTalks();
            CurrentTitle = "Audio Dharma AI: All Talks";
            break;
        case 'GET_ALL_SPEAKERS':
            CurrentTitle = "Audio Dharma AI: All Speakers";
            getAllSpeakers();
            break;
        case 'GET_SIMILAR_TALKS':
            getSimilarTalks(query);
            break;
        case 'GET_SIMILAR_SPEAKERS':
            getSimilarSpeakers(query);
            break;
        case 'GET_SPEAKER_TALKS':
            getSpeakerTalks(query);
            break;
        case 'EXPLORE':
            getExploreResults(query);
            break;
        case 'GET_SERIES_TALKS':
            getSeriesTalks(query);
            break;
        default:
            getAllTalks();
            break;
    }

    const inputElement = document.getElementById('ID_HUMAN_INPUT');

    inputElement.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
        event.preventDefault();
        getExploreInput();
    }
    });
}


function initChat() {

    ChatHistory = "";

    Busy = false;
    initBusyIcon();

    var chatResponseDiv = document.createElement("div");
    chatResponseDiv.className = "CHAT_RESPONSE";
    var chatContainerDiv = document.getElementById("ID_CHAT_CONTAINER");
    chatContainerDiv.appendChild(chatResponseDiv);
    chatContainerDiv.innerHTML = INTRO_CHAT_DIALOG;
}


function initTalk() {

    var searchParams = new URLSearchParams(window.location.search)
    var file_mp3 = searchParams.get('ID');

    $.getJSON(SERVER_ADDRESS,
    {
        'ARG_COMMAND': 'GET_TALK',
        'ARG_QUERY': encodeURIComponent(file_mp3)
    }, function(talk) {

        busyIconStop();

        var url = 'https://audiodharma.us-east-1.linodeobjects.com/talks' + talk['url'];
        var speaker = talk['speaker'];
        var duration = talk['duration'];
        var date = talk['date'];
        var transcript = talk['transcript'];
        var summary = "No current summary.";;
        if ("summary_long" in talk) {
            summary = talk["summary_long"] + "<p><hr>";
        }

        console.log("talk URL: ", url);

        document.getElementById("ID_SITE_ICON").src = talk['url_image_speaker']
        setTitle(talk["title"]);
        document.getElementById("ID_TALK_META").innerHTML = `${speaker} &nbsp;&nbsp;&nbsp&nbsp;&nbsp; ${date} &nbsp;&nbsp;&nbsp&nbsp;&nbsp; ${duration}`;
        document.getElementById("ID_TALK_SUMMARY").innerHTML = summary;
        document.getElementById("ID_TALK_TEXT").innerHTML = transcript;

        var audioElement = document.createElement('audio');
        audioElement.src = url;
        audioElement.controls = true; 
        document.getElementById('ID_AUDIO_PLAYER').appendChild(audioElement);
    });
}


function getAllTalks() {

    console.log("getAllTalks", ListDisplayedTalks.length);

    if (Busy == true) return;

    busyIconStart();
    $.getJSON(SERVER_ADDRESS, {'ARG_COMMAND': "GET_ALL_TALKS", 'ARG_QUERY': ListDisplayedTalks.length })
    .done(function(data) {

        busyIconStop();
        setTitle("All Talks");
        summary = "";
        if ("meta_summary" in data && data["meta_summary"].length > 0) {
            summary = data["meta_summary"] + "&nbsp;&nbsp;&nbsp[Sophia Summary";
            summary = `<strong>${data["meta_summary"]}</strong><p><hr><p>`;
        }
        listTalks = data["list_elements"];
        /*
        if ("summary_long" in data && data["summary_long"].length > 0) {
            meta_summary = "[Sophia's Summary]:&nbsp;&nbsp;" + data["summary_long"]
            html = `<strong>${meta_summary}</strong><p><hr><p>`;
        }
        */
        document.getElementById('ID_SUMMARY').innerHTML = summary;
        displayTalks(listTalks);
        $("#ID_MORE_TALKS").css("visibility", "visible");
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        busyIconStop();
        document.getElementById('ID_ERROR_REPORT').innerHTML = ERROR_SERVICE_OFFLINE;
    });
}


function getAllSpeakers() {

    console.log("getAllSpeakers", ListDisplayedTalks.length);

    if (Busy == true) return;

    busyIconStart();
    $.getJSON(SERVER_ADDRESS, { 'ARG_COMMAND': 'GET_ALL_SPEAKERS'})
    .done(function(data) {

        busyIconStop();
        setTitle("All Speakers");
        var listSpeakers = data["list_elements"]["sorted_alphabetically"];
        displaySpeakers(listSpeakers);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        busyIconStop();
        document.getElementById('ID_SUMMARY').innerHTML = ERROR_SERVICE_OFFLINE;
    });

}


function busyIconStart() {

    $("#ID_BUSY_CONTAINER").css("visibility", "visible");
    Busy = true;
}


function busyIconStop() {

    $("#ID_BUSY_CONTAINER").css("visibility", "hidden");
    Busy = false;
}


function initBusyIcon() {

    const canvas = document.getElementById('ID_BUSY_CANVAS');
    const ctx = canvas.getContext('2d');

    const icon = new Image();
    icon.src = PATH_BUSY_ICON;
    icon.onload = function() {
            
        ctx.drawImage(icon, 0, 0);
    };

    let rotationAngle = 0;
    function animate() {

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.rotate(rotationAngle * Math.PI / 180);
        ctx.drawImage(icon, -icon.width / 2, -icon.height / 2);
        ctx.restore();
        rotationAngle += INC_ROTATION_ANGLE;
        requestAnimationFrame(animate);
    }

    animate();
}

function chatResetButtonActivate() {

    //$("#ID_RESET_CHAT").css("visibility", "visible");
}

function chatResetButtonDeactivate() {

    //$("#ID_RESET_CHAT").css("visibility", "hidden");
}


function displayChatData(question, answer) {

    console.log("displayChatData");
    console.log("answer: ", answer);

    var container = document.getElementById("ID_CHAT_CONTAINER");

    var chatText = answer["responseText"];
    var chatHistory = answer["history"];
    var listTalks = answer["list_talks"];
    var chatHTML;

    ChatHistory = ChatHistory + ' ' + chatHistory + ' ' + chatText;


    var link = "";
    var countLinks = 0;
    for (i = 0; i < listTalks.length; i ++) {

        matchTalk = listTalks[i];
        var title = matchTalk["title"]
        var url = matchTalk["url"]
        var file_mp3 = url.split('/').pop();
        var speaker = matchTalk["speaker"]
        var date = matchTalk["date"]

        // exclude any url previously offered
        if (url in DictTalkExclusions) continue;

        countLinks += 1;
        //if (Math.random() < 0.3) continue;

        link = `<br><a class="CHAT_LINK" href="./talk.html?ID=${file_mp3}">${title} - ${speaker} (${date})</a>`;
        DictTalkExclusions[url] = 0;

    }

    if (link == "") {
        chatHTML = `<p><strong>${question}</strong><p>${chatText}<p><hr class = "SEPARATOR">`;
    } else {
        chatHTML = `<p><strong>${question}</strong><p>${chatText}<p>${link}<hr class = "SEPARATOR">`;
    }

    var chatResponseDiv = document.createElement("div");
    chatResponseDiv.className = "CHAT_RESPONSE";
    chatResponseDiv.innerHTML = chatHTML;

    var chatContainerDiv = document.getElementById("ID_CHAT_CONTAINER");
    if (chatContainerDiv.firstChild) {
        chatContainerDiv.insertBefore(chatResponseDiv, chatContainerDiv.firstChild);
    } else {
        chatContainerDiv.appendChild(chatResponseDiv);
    }

    $("#ID_HUMAN_INPUT").val("");

    //window.scrollTo(0, document.body.scrollHeight);

    chatResetButtonActivate();

}

function displaySpeakers(listSpeakers) {

    console.log("displaySpeakers: ");

    var container = document.getElementById("ID_CONTENT_CONTAINER");
    var html = container.innerHTML;

    for (let speaker of listSpeakers) {

            var name = speaker["title"];
            var count_talks = speaker["count_talks"].toLocaleString();
            var summary_short = speaker["summary_short"];
            var row = `<strong>\n`;
            var col = ``

            col = getScoreDisplayHTML(speaker);
            row += col;

            html = html + `<div style="margin-bottom: 25px; width: 100%">\n`;

            speakerFileName = encodeURIComponent(name);
            var linkSpeakerURL = URL_INDEX_PAGE+'c=GET_SPEAKER_TALKS&q='+speakerFileName;
            col = `<a style="margin-right: 15px; color: black" href=${linkSpeakerURL}>${name}</a>\n`
            row += col;
            col = `<span style="margin-right: 10px" >${count_talks} Talks</span>\n`
            row += col;
            //col = `<span style="position: absolute; top: 0; right: 0;" >${duration}</span>\n`
            //row += col;
            row += `</strong>\n`;
            html += row;
            
            var linkSimilarURL = URL_INDEX_PAGE+'c=GET_SIMILAR_SPEAKERS&q='+speakerFileName;
            linkSimilar = `<a class="MATCH_LINK" href=${linkSimilarURL}>Similar Speakers</a>`;
            //linkDifferent = `<a class="MATCH_LINK" href=${linkDifferentURL}>Different Talks</a>`;
            html += `<div>${summary_short}</div>\n`;
            //html += `<div style="width: 100%; xbackground-color: red">xxx</div>\n`;
            console.log(html);
            
            html += linkSimilar;

            html += `</div>\n`;
     }
     html += `</div>\n`;
    var html = html + "<hr><br></div>\n";
    container.innerHTML = html;
}



function displayTalks(listTalks) {

    console.log("displayTalks");

    var container = document.getElementById("ID_CONTENT_CONTAINER");

    if (listTalks.length == 0) {
        container.innerHTML = "<p><hr>There are no relevant talks<p>";
        return 0;
    }
    var html = "<p>";

    for (let talk of listTalks) {
            var url = talk["url"];
            var title = talk["title"];
            var speaker = talk["speaker"];
            var summaryBrief = talk["summary_brief"];
            var date = talk["date"];
            var duration = talk["duration"];
            var series = talk['series']

            var fileMP3 = url.split('/').pop();
            var encodedTalkID = encodeURIComponent(fileMP3);
            var speakerFileName = encodeURIComponent(speaker);
            var linkSpeakerURL = URL_INDEX_PAGE+'c=GET_SPEAKER_TALKS&q='+speakerFileName;
            var linkSeriesURL = URL_INDEX_PAGE+'c=GET_SERIES&q='+encodeURIComponent(series);
            var displayedScore = getScoreDisplayHTML(talk);
            
            console.log("displayedScore: ", displayedScore);

            var linkSimilarTalkURL = URL_INDEX_PAGE+'c=GET_SIMILAR_TALKS&q='+encodeURIComponent(fileMP3)
            var linkSimilarTalk = `<a class="MATCH_LINK" href=${linkSimilarTalkURL}>Similar Talks</a>`;

            var linkSeriesURL = URL_INDEX_PAGE+'c=GET_SERIES_TALKS&q='+encodeURIComponent(series)
            var linkSeries = `<a class="MATCH_LINK" href=${linkSeriesURL}>Series</a>`;

            var linkSimilarSpeakerURL = URL_INDEX_PAGE+'c=GET_SIMILAR_SPEAKERS&q='+encodeURIComponent(speaker)
            var linkSimilarSpeaker = `<a class="MATCH_LINK" href=${linkSimilarSpeakerURL}>Similar Speakers</a>`;

            html += `<div style="margin-bottom: 25px">\n`;

            html +=  `\n<strong>${displayedScore}\n 
            <span style="margin-right: 10px">\n
            ${date}</span> <a style="margin-right: 15px; color: black" href=${linkSpeakerURL}>${speaker}</a>\n
            <a style="margin-right: 15px; color: black" href="./talk.html?ID=${encodedTalkID}">${title}</a>  <span style="margin-right: 10px" >${duration}</span> </strong>`;

            html += `<div>${summaryBrief}</div>\n`;
            html += `${linkSimilarTalk} &nbsp;&nbsp;&nbsp; ${linkSimilarSpeaker}`;

            if (series.length > 1) {
                html += `&nbsp;&nbsp;&nbsp;${linkSeries}`;
            }

            html += `</div>\n`;
    }
    var html = html + "</div>\n";
    container.innerHTML = html;

    ListDisplayedTalks.push(...listTalks);
    return listTalks.length;
}


function getExploreResults(query) {

    console.log("getExploreResults");

    if (query.length < MIN_HUMAN_INPUT_LENGTH) {
        getAllTalks();
        return;
    }

    if (Busy == true) return;

    busyIconStart();

    $.getJSON(SERVER_ADDRESS, { 'ARG_COMMAND': "GET_EXPLORE", 'ARG_QUERY': query})
    .done(function(data) {
        console.log(data);

        busyIconStop();
        var ai_response = data["ai_response"];
        document.getElementById('ID_SUMMARY').innerHTML = ai_response;
        console.log(ai_response);

        console.log('QUERY: ', query);
        setTitle(query);
        var listTalks = data["list_elements"];
        if ("list_elements" in data) {
            listTalks = data["list_elements"];
            displayTalks(listTalks);
        }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        busyIconStop();
        document.getElementById('ID_ERROR_REPORT').innerHTML = ERROR_SERVICE_OFFLINE;
    });

}


function getExploreInput() {

    console.log("getExplore");

    var  question, speaker, quote;

    if (Busy == true) return;

    busyIconStart();
    busyIconStop();

    question =  $("#ID_HUMAN_INPUT").val();
    question = encodeURIComponent(question);
    /*
    question = encodeURIComponent(question);
    if (question.length < MIN_HUMAN_INPUT_LENGTH) return;
    */

    //CJM DEV
    var command = `${DEV_URL_BASE}?c=EXPLORE&q=${question}`;
    console.log(command);
    window.location.assign(command);
}


function getSimilarTalks(file_mp3) {

    console.log("getSimilarTalks: " + file_mp3);

    if (Busy == true) return;

    busyIconStart();
    $.getJSON(SERVER_ADDRESS, {'ARG_COMMAND': "GET_SIMILAR_TALKS", 'ARG_QUERY': encodeURIComponent(file_mp3) })
    .done(function(data) {

        busyIconStop();

        var ai_response = "[No commentary available]";
        if ("ai_response" in data) {
            summary = data["ai_response"];
        }
        document.getElementById('ID_SUMMARY').innerHTML = summary;
        
        if ("list_elements" in data) {

            setTitle(`${data["title"]}<br>Similar Talks`);
            displayTalks(data["list_elements"]);
        } else {
            document.getElementById('ID_PAGE_TITLE').innerHTML = `Similar Talks - Update in Progress`

        }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        busyIconStop();
        document.getElementById('ID_ERROR_REPORT').innerHTML = ERROR_SERVICE_OFFLINE;
    });

}


function getSimilarSpeakers(speaker) {

    console.log("getSimilarSpeakers: " + speaker);

    if (Busy == true) return;

    busyIconStart();
    $.getJSON(SERVER_ADDRESS, { 'ARG_COMMAND': "GET_SIMILAR_SPEAKERS", 'ARG_QUERY': encodeURIComponent(speaker)})
    .done(function(data) {

        console.log(data);
        busyIconStop();

        setTitle(data["title"] + "<br>Similar Speakers");

        var summary = "No Summary Available"
        if ("summary_short" in data && data["summary_short"].length > 0) {
            summary = data["summary_short"]
        }

        //document.getElementById("ID_SUMMARY").innerHTML = `${summary}<p><hr>`;

        var listSpeakers = data["list_elements"]
        console.log(listSpeakers);
        displaySpeakers(listSpeakers);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        busyIconStop();
        document.getElementById('ID_ERROR_REPORT').innerHTML = ERROR_SERVICE_OFFLINE;
    });
}


function getSeriesTalks(series) {

    console.log("getSeriesTalks: " + series);

    if (Busy == true) return;
    busyIconStart();

    $.getJSON(SERVER_ADDRESS, { 'ARG_COMMAND': "GET_SERIES_TALKS", 'ARG_QUERY': encodeURIComponent(series) })
     .done(function(data) {
        busyIconStop();

        document.getElementById('ID_PAGE_TITLE').innerHTML = "Series:&nbsp;" + data["title"];
        listTalks = data["list_elements"];
        displayTalks(listTalks);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        busyIconStop();
        document.getElementById('ID_ERROR_REPORT').innerHTML = ERROR_SERVICE_OFFLINE;
    });

}


function getSpeakerTalks(speaker) {

    console.log("getSpeakerTalks: " + speaker);

    if (Busy == true) return;


    busyIconStart();
    var speakerFileName = encodeURIComponent(speaker);
    $.getJSON(SERVER_ADDRESS, { 'ARG_COMMAND': "GET_SPEAKER_TALKS", 'ARG_QUERY': encodeURIComponent(speaker)}) 
    .done(function(data) {

        console.log("getSeakerTalks: " + data);
        busyIconStop();
        setTitle(data["title"] + "<br>All Talks");
        document.getElementById('ID_SUMMARY').innerHTML = data["summary_long"];

        var listTalks = data["list_elements"];
        if (listTalks.length > 0){
            var url_image_speaker = listTalks[0]['url_image_speaker'];
            console.log("image: ", url_image_speaker);
            document.getElementById("ID_SITE_ICON").src = url_image_speaker;
        }
        displayTalks(listTalks);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        busyIconStop();
        document.getElementById('ID_ERROR_REPORT').innerHTML = ERROR_SERVICE_OFFLINE;
    });
}


function deleteChatSession() {

    console.log("deleteChatSession");

    $("#ID_HUMAN_INPUT").val("");
    var container = document.getElementById("ID_CHAT_CONTAINER");
    container.innerHTML = "";
    chatResetButtonDeactivate();

    /*
     * DEV:  do not reset internal chat history, just visible chat history
     * May want to return to this at some later point
     */
    //ChatHistory = ''

}


function askChatQuestion() {

    console.log("startChatSession");

    if (Busy == true) return;
    busyIconStart();

    const question =  $("#ID_HUMAN_INPUT").val();

    $.getJSON(SERVER_ADDRESS, { 'ARG_COMMAND': "CHAT", 'ARG_QUERY': question, 'ARG_HISTORY': encodeURIComponent(ChatHistory)})
    .done(function(data) {

        console.log(data);
        displayChatData(question, data);
        busyIconStop();
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        busyIconStop();
        document.getElementById('ID_SUMMARY').innerHTML = ERROR_SERVICE_OFFLINE;
    });
}


function getScoreDisplayHTML(element) {

    var html = ''
    if ('score' in element) {
        var score = Math.floor(element['score'] * 100);
        var scoreColorID;;
        const scorePercentage = parseFloat(score);

        if (scorePercentage >= 80) {
            scoreColorID = "ID_SCORE_HIGH";
        }
        else if (scorePercentage >= 60) {
            scoreColorID = "ID_SCORE_MEDIUM";
        }
        else {
            scoreColorID = "ID_SCORE_LOW";
        }
        html = `<span id="${scoreColorID}" style="margin-right: 10px" >${score}%</span>\n`;
    }

    return(html);
}


function setTitle(title) {

    console.log("setTitle: ", title);
    if (document.getElementById("ID_PAGE_TITLE")) {
        document.getElementById('ID_PAGE_TITLE').innerHTML = title;
    } else {
        document.getElementById('ID_TALK_TITLE').innerHTML = title;
    }
    CurrentTitle = title;
}


function shareViaEmail() {

    var address = "";
    var subject = "AudioDharma.ai: \n\n" + CurrentTitle.replace("<br>", " ");
    var emailBody = "\n\n" + window.location.href + "\n\nAudioDharma.ai: Artificial Intelligence meets The Dharma";
    var encodedBody = encodeURIComponent(emailBody);

    var mailtoLink = "mailto:" + address + "?subject=" + subject + "&body=" + encodedBody;
    window.open(mailtoLink, '_blank');
}





