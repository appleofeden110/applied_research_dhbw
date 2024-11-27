# Scrapper+Crawler for Applied Market Research 

## Installation 

```shell
pip
```

## Usage

```shell
python ./scrapper/main.py "[media markt.de url]" 
```

## Description 

This is created as a proof of concept, kind of an alpha version of the actual bot that will be submitted with data as well during the submission date.

For now it is only accepting MediaMarkt.de URLs and does not work with any other platform. That is, however, going to change. 

## Warnings

Generally speaking, you might encounter something of this sort of error when trying the bot

```shell
Error clicking next page: Message: no such element: Unable to locate element: {"method":"xpath","selector":".//button[contains(., "Nächste Seite")]"}
  (Session info: chrome=130.0.6723.60); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception
Stacktrace:
        GetHandleVerifier [0x00007FF666E53AB5+28005]
        (No symbol) [0x00007FF666DB83B0]
        (No symbol) [0x00007FF666C5580A]
        (No symbol) [0x00007FF666CA5A3E]
        (No symbol) [0x00007FF666CA5D2C]
        (No symbol) [0x00007FF666C9937C]
        (No symbol) [0x00007FF666CCBA7F]
        (No symbol) [0x00007FF666C99246]
        (No symbol) [0x00007FF666CCBC50]
        (No symbol) [0x00007FF666CEB8B3]
        (No symbol) [0x00007FF666CCB7E3]
        (No symbol) [0x00007FF666C975C8]
        (No symbol) [0x00007FF666C98731]
        GetHandleVerifier [0x00007FF66714643D+3118829]
        GetHandleVerifier [0x00007FF667196C90+3448640]
        GetHandleVerifier [0x00007FF66718CF0D+3408317]
        GetHandleVerifier [0x00007FF666F1A40B+841403]
        (No symbol) [0x00007FF666DC340F]
        (No symbol) [0x00007FF666DBF484]
        (No symbol) [0x00007FF666DBF61D]
        (No symbol) [0x00007FF666DAEB79]
        BaseThreadInitThunk [0x00007FFE59F67374+20]
        RtlUserThreadStart [0x00007FFE5AA9CC91+33]

Could not proceed to next page after page 6

```

We could not find a smooth solution to this problem, but essentially it is just showing that it cannot read more reviews than there is on the page. It will be turned into a smooth logging line, however at the moment it is as it is. 

We would love to hear your feedback. 

Data Science Team