# function to get userAgents into an array from userAgent.txt file

function getArray() {
    userAgentList=() # Create empty array
    while IFS= read -r line # Read in lines one by one
    do
        userAgentList+=("$line") # Append line to the array
    done < "$1"
}

getArray "~/PolBot/txt/userAgents.txt"

# function to select a random user agent
function randArrayElement(){ arr=("${!1}"); echo ${arr[$[RANDOM % ${#arr[@]}]]}; }

# function to execute curl with random user agents
curlMarkets() {
	inputList=$1
	inputList=($@)
	ind=`expr ${#inputList[@]} - 2`
	for i in `seq 0 $ind`; 
	do
		userAgent=$(randArrayElement "userAgentList[@]")
		# echo $userAgent
		# echo ${inputList[$i]}
		curl -A "$userAgent" ${inputList[$i]} -o ${inputList[$i+1]}
	done
}

