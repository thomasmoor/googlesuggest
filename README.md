# googlesuggest

The autocomplete in Google Search is a great tool to find new ideas.
One technique used by bloggers and video creators is to type a topic like dogs followed by a space and letters
Like first a, which gives you dogs and cats, dogs anatomy... Then b, which gives you dogs breeds, dogs barking...
You can continue with all the letters of the alphabet

The problem is that it is time consuming and you cannot copy paste the suggestions

Google actually offers an api at suggestqueries.google.com
You can call it directly from a program, for example: http://suggestqueries.google.com/complete/search?client=firefox&hl=en&q=dogs a
And it retrieves the data in a computer readable format.

So I developed this tool that automatically queries Google Suggest

It is available on my website thomasmoor.org and then select "Google Suggest"

You enter a keyword, like dogs, to follow our previuous example
You select the letters that you want to append to your keyword, for example dogs followed by a, then by by, then by c
The programs then goes and retrieves all the suggestions and displays them on the screen.

And press the Download button to save the data to file
