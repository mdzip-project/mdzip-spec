# Hostile content

Test document for consumer conformance test `T-016` (Sections 9.2, 9.3 and 13.2). Each block below tries to run a script, load a resource or navigate on its own. If one succeeds, it requests `http://127.0.0.1:18766/<case-id>` — the *canary*. A harness serves that address, renders this document, and checks that the canary received none of the requests marked as forbidden in `examples/fixtures/hostile-content-cases.json`.

The archive's own image must still render:

![archive image](images/ok.png)

## script-element

<script>new Image().src = 'http://127.0.0.1:18766/script-element';</script>

## event-handler

<img src="images/missing.png" alt="event-handler" onerror="new Image().src = 'http://127.0.0.1:18766/event-handler'">

## svg-inline-script

<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" onload="new Image().src = 'http://127.0.0.1:18766/svg-inline-script'"><script>new Image().src = 'http://127.0.0.1:18766/svg-inline-script';</script></svg>

## svg-file-script

![svg-file-script](images/script.svg)

## javascript-link

[javascript-link](javascript:void(new%20Image().src='http://127.0.0.1:18766/javascript-link'))

## base-element

<base href="http://127.0.0.1:18766/base-element/">

![base-element](images/ok.png)

## meta-refresh

<meta http-equiv="refresh" content="0; url=http://127.0.0.1:18766/meta-refresh">

## stylesheet-link

<link rel="stylesheet" href="http://127.0.0.1:18766/stylesheet-link">

## style-url

<p style="background-image: url('http://127.0.0.1:18766/style-url')">style-url</p>

## iframe

<iframe src="http://127.0.0.1:18766/iframe"></iframe>

## object-embed

<object data="http://127.0.0.1:18766/object-embed"></object>
<embed src="http://127.0.0.1:18766/object-embed">

## http-image

![http-image](http://127.0.0.1:18766/http-image)
