# Member-Selection

Program used to select members for UCL Hiking Club's residential trips

-n inidicates number of spaces avalible
-p provides a list of names that are pre-approved, i.e. committee and walk leaders
-f indicates the file location to use
-r indicates that the list of eligible but not selected members should be drawn from

Only one of -r and -f should be provided.

This code is highly experimental and not tested, so should be treated with caution.

Common example command might be:
python3 selector.py -n 15 -p 'Jonas, Shamin Tahasildar' -f 'Sign Up (Responses).xlsx'

Requires pandas library.

May also not provide arguments and they will be taken from input.