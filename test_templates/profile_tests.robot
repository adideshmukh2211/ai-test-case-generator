*** Settings ***
Documentation     Common test cases for user profile management
Library          SeleniumLibrary

*** Variables ***
${URL}                  https://example.com/profile
${BROWSER}              chrome
${PROFILE_PIC_INPUT}    //input[@type='file']
${BIO_FIELD}           //textarea[@name='bio']
${SAVE_BUTTON}         //button[contains(text(),'Save')]
${SUCCESS_MESSAGE}     //div[contains(@class,'success')]
${ERROR_MESSAGE}       //div[contains(@class,'error')]

*** Test Cases ***
Update Profile Picture
    [Documentation]    Test uploading a new profile picture
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    Choose File    ${PROFILE_PIC_INPUT}    ${CURDIR}/test_data/valid_image.jpg
    Wait Until Element Is Visible    ${SUCCESS_MESSAGE}
    Page Should Contain    Profile picture updated
    [Teardown]    Close Browser

Update Bio Information
    [Documentation]    Test updating user bio
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    Clear Element Text    ${BIO_FIELD}
    Input Text    ${BIO_FIELD}    This is a test bio with updated information
    Click Element    ${SAVE_BUTTON}
    Wait Until Element Is Visible    ${SUCCESS_MESSAGE}
    Page Should Contain    Profile updated successfully
    [Teardown]    Close Browser

Invalid Image Format
    [Documentation]    Test uploading invalid image format
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    Choose File    ${PROFILE_PIC_INPUT}    ${CURDIR}/test_data/invalid_file.txt
    Wait Until Element Is Visible    ${ERROR_MESSAGE}
    Page Should Contain    Invalid file format
    [Teardown]    Close Browser

Bio Character Limit
    [Documentation]    Test bio character limit
    Open Browser    ${URL}    ${BROWSER}
    Maximize Browser Window
    ${LONG_BIO}=    Set Variable    ${'x' * 501}
    Input Text    ${BIO_FIELD}    ${LONG_BIO}
    Click Element    ${SAVE_BUTTON}
    Wait Until Element Is Visible    ${ERROR_MESSAGE}
    Page Should Contain    Bio cannot exceed 500 characters
    [Teardown]    Close Browser
