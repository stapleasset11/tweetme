import React, {useEffect,useState} from "react";

import { loadTweets } from "../lookup/components";

  export function TweetList(props){
  
    const [tweets,setTweets] = useState([])
    useEffect(() => {
      const myCallback = (response,status) => {
        
        if (status === 200){
          setTweets(response)
        } else {
          alert("There was an error")
        }
  
      }
  
      loadTweets(myCallback)
  
    } ,[])
    return tweets.map((item,index)=> {
      return <Tweet tweet={item} className="my-5 py-5 border rounded-lg bg-grey text-white" key={`${index}-{item.id}`}/>
      })
  
  }



export function ActionBtn(props){
    const {tweet,action} = props
    const [likes,setLikes] = useState(tweet.likes ? tweet.likes:0)
    const [userLike,setUserLike] = useState(tweet.userLike===true ? true:false)
    const className = props.className ? props.className: 'btn btn-primary btn-small'
    const actionDisplay = action.display ? action.display : 'Action'
    const display = action.type === 'like' ?  `${likes} ${actionDisplay}`: actionDisplay
    const handleClick = (event) => {
        event.preventDefault()
        if (action.type === "like") {
            if (userLike === true){
                setLikes(likes - 1)
                setUserLike(false)
            } else {
                setLikes(tweet.likes+1)
                setUserLike(true)
            }
            // setLikes(tweet.likes+1)
        }
    }
    return <button className={className} onClick={handleClick}>{display}</button>
  //  return "<button class='btn btn-primary btn-small' onclick='handleTweetActionBtn(" + tweet.id + ", " + tweet.likes + ", \"like\")'>" + tweet.likes + " likes</button>;
  }
  
  
  export function Tweet(props){
    const {tweet} = props
    const className = props.className ? props.className: "col-10 col-md-6 mx-auto"
    // const action = {type:"like"}
  
    return <div className={className}>
      <p>{tweet.id} - {tweet.content}</p>
      <div className="btn btn-group">
        <ActionBtn tweet={tweet} action={{type:"like",display:"likes"}}/>
        <ActionBtn tweet={tweet} action={{type:"unlike",display:"unlike"}}/>
        <ActionBtn tweet={tweet} action={{type:"retweet",display:"retweet"}}/>
      </div>
    </div>
  }