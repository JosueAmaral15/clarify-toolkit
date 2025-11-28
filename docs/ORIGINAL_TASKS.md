 Programming Tasks:
    
    MUST HAVE
        TASKS DONE
            [X] implement threads to search files;
            [X] include single files and not only directories;
            [X] replace text from dropdown relative to insert panel;
            [X] solve the following issue "json.decoder.JSONDecodeError: Expecting ':' delimiter: line 4629 column 21 (char 185171)"
            [X] dont override: avoid JSON Translate processing which the translate overrides translate names (e.g.: {t.pages.Prac{t.pages.Navbar.blog}HistoryPage.blank}Lin{t.pages.BlogPage.read});
            [X] ajust the JSON Translate to translate only in a code scope (and don't anymore). The example: 'children: React.React{t.pages.translation.buttons.no}de' is not a text to be translated, when it keep as following like children: React.ReactNode;
            [X] first object variable name: the JSON Translate is not sufficient to cover all algorithm translation problems, since the name t, which is the root, must be specified, where the input parameters can customize the root name.
            [X] add possibility to use regular expression in replacement to don't replace some characters, only what's needs;

        TASKS TO-DO
            [] fix serious problem with the JSON Rewriter, which some data is lost after processing, omitting some keys and values;
            [] add scope in the conditional advanced options in algorithm case, for example, only between brackets;
            [] avoid this behavior: {t.pages.onboarding.navigationHints.skip} if stuck - unanswered = zero {t.pages.PracticeHistoryPage.points};
    SHOULD HAVE
        TASKS DONE
        
        TASKS TO-DO
            [] include the possibility to use the three following checkbox options in the conditional advanced options: case sensitive, match whole word and regular expression;
            [] add scope in the conditional advanced options in algorithm case, for example, only between brackets;
            [] include search and character lookup in the Insert panel tab for inserting characters with search and lookup instead of defining the line number in which the text should be inserted.
            [] add JSON translation reversal functionality;
            [] add the ability to right-click to open some options in the match panel: copy, copy all, select all, open file, and open all files. When the user click with CTRL or shift buttons pressioned, the application must select all the results which the user select with the mouse;
                'Why it\'s wrong:',
                'Why it\'s wrong:'
            ],
            
            [] add feature to replace lists for only objects or dictionaries in JSON files with scope restrictions, like only in t.pages;
            [] add feature to interrupt processing while loading results;
            [] include the possibility to list the files with ls or dir parameters with advanced search tools;
            [] Insertion of files and directories in an asynchronous and selectable way, so that it does not matter how many files are selected and in which directories they are.
            [] include query to artificial intelligence without files or directories, only with user text;
            [] identify tags, curle backets, square brackets and parenthesis to avoid errors in JSON Rewriter and to text editor use;
            [] include a advanced search which the user can search with multiple queries separated by new lines with the possibility to use regular expressions. Each line would be a new search query;
            [] remove the following errors: ```typescript and ``` in the output while using IA query;
            [] include search where the word key have count of occurrences, for example, only the keys which have more than 2 occurrences. Use relational operations;
            [] the Interrupt Request in ChatGPT File Processor don't works. Solve this issue.
            [] need to solve the translating issue when the text have parenthesis, example: 'Multiple Choice (Multiple)';
            [] avoid the problem that JSON Translate don't replace the object keys from affect files when removing keys from dictionary, making a keys omision and consequently the 'undefined' error;

    COULD HAVE
        TASKS DONE
        
            [] add the feature which the result can be reused on clarify text edit;
            [] possibility search for JSON keys and values with the following example: t.auth.brandTitle;
            [] include 'is file' in other places to take more files with directory paths;
    
            [] add new feature to insert new keys and values in existing keys with regular expression and memory register concept; 
            [] include the possibility to insert a new value in group mode, which word keys can be used to insert the new value between these word keys, in separated line (new line) or in a specific column. The user could enter the occurrences count tolerated to allow the insert (threshold);
            [] add the possibility to rewrite the JSON replacing the key and object in other places if the value of the key is the same and the keys have different.
            [] Allow the user to choose className names instead of tag names to make the JSON keys; The user can choose get only the difference between the className names for this occasion;
 
    WOULD HAVE LATER
        TASKS DONE
        
        TASKS TO-DO
            [] include 'clear all conditions' button in conditional advanced options;
            [] add scroll in 'search/replace' and 'insert' panels;
            [] including activity history like Google Translate feature;
            [] include the possibility of adding a new line of conditional advanced options, with a minimum of 3 and no maximum limit.
            [] provide the ability to change the application's appearance to a transparent background;
            [] change the insert text, query and replacement text boxes to a text box that can be resized by the user;
            [] add the options to undo and redo the changes made;
            [] Translate the application into the world's most spoken languages;
            [] Calculator: Add calculator concepts such as memory register, addition, concatenation, and standard memory recall with modification history.
            [] Set: Add logical set operations from file j1 such as intersection, difference, union, and exclusive difference. Include checkboxs to include keys and/or values in this set operation;
            [] Include usage tutorials;
            [] Include search with artificial intelligence help;
            [] Embed a virtual assistant for use with AI;
            [] Include AI usage fee of 50% more than the actual amount for my account + 1% to remain in the cash bank, as the user must make the payment using AI, totaling around 151% of the actual amount to be paid. Inform the user that they pay in tokens;
            [] Research the possibility of embedding Clarify in the Linux application manager and how much you earn by doing so. Once installed, compile the code before sending;
            [] Add user data backup for undo and redo with ECC, or, whether or not, use Gof command architecture;
            [] add data backup with command arquitecture, with Egg Cell Compactor and artificial intelligence to store all the changes made by the user even for a long period of time;
            [] Allow user to make macros and algorithms with the application features for more complex utilities, with Python code or block programming;
            [] When the user click in a search result or in a insert result, the application could have to open the file in a own file editor;
            [] Make the Clarify able to create algorithms to perform some user tasks, and not only, also compile or an translate to a programming language (like Python, React and Javascript)