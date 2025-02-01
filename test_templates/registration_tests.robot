*** Settings ***
Documentation     Common test cases for user registration
Library          SeleniumLibrary

*** Variables ***
${URL}                  https://example.com/register
${BROWSER}              chrome
${EMAIL_FIELD}          //input[@type='email']
${PASSWORD_FIELD}       //input[@type='password']
${CONFIRM_PASS_FIELD}   //input[@name='confirm_password']
${USERNAME_FIELD}       //input[@name='username']
${REGISTER_BUTTON}      //button[@type='submit']
${SUCCESS_MESSAGE}      //div[contains(@class,'success')]
${ERROR_MESSAGE}        //div[contains(@class,'error')]

*** Test Cases ***
Valid Registration
    [Documentation]    Test registration with valid information
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    Input Text    ${USERNAME_FIELD}    testuser123
    Input Text    ${EMAIL_FIELD}    test@example.com
    Input Text    ${PASSWORD_FIELD}    SecurePass123!
    Input Text    ${CONFIRM_PASS_FIELD}    SecurePass123!
    Click Element    ${REGISTER_BUTTON}
    Wait Until Element Is Visible    ${SUCCESS_MESSAGE}
    Page Should Contain    Registration successful
    [Teardown]    Close Browser

Password Mismatch
    [Documentation]    Test registration with mismatched passwords
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    Input Text    ${USERNAME_FIELD}    testuser123
    Input Text    ${EMAIL_FIELD}    test@example.com
    Input Text    ${PASSWORD_FIELD}    Password123!
    Input Text    ${CONFIRM_PASS_FIELD}    DifferentPass123!
    Click Element    ${REGISTER_BUTTON}
    Wait Until Element Is Visible    ${ERROR_MESSAGE}
    Page Should Contain    Passwords do not match
    [Teardown]    Close Browser

Weak Password
    [Documentation]    Test registration with weak password
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    Input Text    ${USERNAME_FIELD}    testuser123
    Input Text    ${EMAIL_FIELD}    test@example.com
    Input Text    ${PASSWORD_FIELD}    weak
    Input Text    ${CONFIRM_PASS_FIELD}    weak
    Click Element    ${REGISTER_BUTTON}
    Wait Until Element Is Visible    ${ERROR_MESSAGE}
    Page Should Contain    Password must be at least 8 characters
    [Teardown]    Close Browser

Existing Email
    [Documentation]    Test registration with existing email
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    Input Text    ${USERNAME_FIELD}    newuser123
    Input Text    ${EMAIL_FIELD}    existing@example.com
    Input Text    ${PASSWORD_FIELD}    SecurePass123!
    Input Text    ${CONFIRM_PASS_FIELD}    SecurePass123!
    Click Element    ${REGISTER_BUTTON}
    Wait Until Element Is Visible    ${ERROR_MESSAGE}
    Page Should Contain    Email already registered
    [Teardown]    Close Browser
