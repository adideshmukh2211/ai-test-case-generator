*** Settings ***
Documentation     Common test cases for login functionality
Library          SeleniumLibrary

*** Variables ***
${URL}           https://example.com
${BROWSER}       chrome
${VALID_USER}    test@example.com
${VALID_PASS}    Password123
${LOGIN_BUTTON}  //button[@type='submit']
${EMAIL_FIELD}   //input[@type='email']
${PASS_FIELD}    //input[@type='password']

*** Test Cases ***
Valid Login
    [Documentation]    Test login with valid credentials
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    Input Text      ${EMAIL_FIELD}    ${VALID_USER}
    Input Text      ${PASS_FIELD}     ${VALID_PASS}
    Click Element   ${LOGIN_BUTTON}
    Page Should Contain Element    //div[contains(@class,'dashboard')]
    [Teardown]    Close Browser

Invalid Email Format
    [Documentation]    Test login with invalid email format
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    Input Text      ${EMAIL_FIELD}    invalid.email
    Input Text      ${PASS_FIELD}     ${VALID_PASS}
    Click Element   ${LOGIN_BUTTON}
    Page Should Contain    Invalid email format
    [Teardown]    Close Browser

Empty Password
    [Documentation]    Test login with empty password
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    Input Text      ${EMAIL_FIELD}    ${VALID_USER}
    Click Element   ${LOGIN_BUTTON}
    Page Should Contain    Password is required
    [Teardown]    Close Browser
