# Video Transcription

**Detected Language:** en
**Language Probability:** 1.00

## Transcription Content

**[00:01 - 00:12]**

[music]

**[00:13 - 00:16]**

>> Hey everyone. I'm Vic and I lead applied research at

**[00:16 - 00:19]**

I'm Vic and I lead applied research at LangChain and I'm going to talk about

**[00:19 - 00:22]**

LangChain and I'm going to talk about something that I think is sexy, which is

**[00:22 - 00:24]**

something that I think is sexy, which is data mining, but it's not as sexy as

**[00:24 - 00:26]**

data mining, but it's not as sexy as LLM, so we're going to try to like make

**[00:26 - 00:28]**

LLM, so we're going to try to like make it sexy together. And the problem that

**[00:28 - 00:30]**

it sexy together. And the problem that we're going to talk about today is how

**[00:30 - 00:33]**

we're going to talk about today is how do we continuously improve agents, but

**[00:33 - 00:35]**

do we continuously improve agents, but how do we do that via data?

**[00:35 - 00:38]**

how do we do that via data? So, to start, I'm going to tell a little

**[00:38 - 00:40]**

So, to start, I'm going to tell a little story that I think maybe a lot of us

**[00:40 - 00:44]**

story that I think maybe a lot of us have felt before. Like, I ran my agent,

**[00:44 - 00:46]**

have felt before. Like, I ran my agent, it did a bunch of things,

**[00:46 - 00:49]**

it did a bunch of things, it made some mistakes.

**[00:49 - 00:50]**

it made some mistakes. Now, I ask someone like, what do I

**[00:50 - 00:52]**

Now, I ask someone like, what do I actually do about that? Like, I have all

**[00:52 - 00:56]**

actually do about that? Like, I have all this data, made some mistakes, what now?

**[00:56 - 00:58]**

this data, made some mistakes, what now? Basically, what we're going to do today

**[00:58 - 01:00]**

Basically, what we're going to do today is we're going to motivate a recipe for

**[01:00 - 01:02]**

is we're going to motivate a recipe for what we should do to continuously

**[01:02 - 01:04]**

what we should do to continuously improve agents over time, and then I'm

**[01:04 - 01:06]**

improve agents over time, and then I'm going to talk from some lived experience

**[01:06 - 01:07]**

going to talk from some lived experience and like some stuff that we help

**[01:07 - 01:09]**

and like some stuff that we help customers do to run this over

**[01:09 - 01:11]**

customers do to run this over large-scale trace data.

**[01:11 - 01:13]**

large-scale trace data. So, the first step in building a

**[01:13 - 01:17]**

So, the first step in building a successful agent is shipping it. So, if

**[01:17 - 01:18]**

successful agent is shipping it. So, if you put it out into the real world, then

**[01:18 - 01:20]**

you put it out into the real world, then it can operate in environments and then

**[01:20 - 01:21]**

it can operate in environments and then you can get feedback from what it's

**[01:21 - 01:23]**

you can get feedback from what it's doing.

**[01:23 - 01:26]**

doing. The second step is collect a ton of

**[01:26 - 01:28]**

The second step is collect a ton of traces. So, agents operate in the

**[01:28 - 01:30]**

traces. So, agents operate in the environment every single time they

**[01:30 - 01:32]**

environment every single time they operate, they do tool calls, they have

**[01:32 - 01:34]**

operate, they do tool calls, they have output messages, they call APIs, they

**[01:34 - 01:37]**

output messages, they call APIs, they use CLIs. All of that generates data and

**[01:37 - 01:38]**

use CLIs. All of that generates data and we want to store all of that so we can

**[01:38 - 01:42]**

we want to store all of that so we can like do stuff with it.

**[01:42 - 01:44]**

like do stuff with it. The next thing is the data mining in

**[01:44 - 01:47]**

The next thing is the data mining in this talk, which is once we have tons of

**[01:47 - 01:49]**

this talk, which is once we have tons of trace data, maybe gigabytes, maybe

**[01:49 - 01:51]**

trace data, maybe gigabytes, maybe terabytes, depending on like how many

**[01:51 - 01:52]**

terabytes, depending on like how many agents you're shipping, we're going to

**[01:52 - 01:55]**

agents you're shipping, we're going to do data mining over that. And I promise

**[01:55 - 01:56]**

do data mining over that. And I promise I will tell you exactly what data mining

**[01:56 - 01:58]**

I will tell you exactly what data mining we're going do, uh but we're going to do

**[01:58 - 02:00]**

we're going do, uh but we're going to do some over it.

**[02:00 - 02:02]**

some over it. And then the fun part, which is I

**[02:02 - 02:04]**

And then the fun part, which is I collected that data, I read it, I

**[02:04 - 02:06]**

collected that data, I read it, I curated it, and now we actually need to

**[02:06 - 02:09]**

curated it, and now we actually need to run the experiments in a data-driven way

**[02:09 - 02:11]**

run the experiments in a data-driven way to see, "Hey, is this new prompt, or is

**[02:11 - 02:13]**

to see, "Hey, is this new prompt, or is this new tool, or is this new

**[02:13 - 02:15]**

this new tool, or is this new orchestration, or is this new loop, is

**[02:15 - 02:17]**

orchestration, or is this new loop, is it actually improving things based on

**[02:17 - 02:21]**

it actually improving things based on the previous traces that I've seen?"

**[02:24 - 02:26]**

And this is maybe a bit of a hot take, but continual learning is super hot

**[02:26 - 02:27]**

but continual learning is super hot right now. I'm talking about it, this

**[02:27 - 02:29]**

right now. I'm talking about it, this whole room is going to hear about it for

**[02:29 - 02:32]**

whole room is going to hear about it for the next like 5-6 hours. Um but there's

**[02:32 - 02:34]**

the next like 5-6 hours. Um but there's a very tight coupling between what

**[02:34 - 02:36]**

a very tight coupling between what observability is and what continual

**[02:36 - 02:38]**

observability is and what continual learning is. And the main reason for

**[02:38 - 02:40]**

learning is. And the main reason for that is that

**[02:40 - 02:42]**

that is that agents that operate in environments,

**[02:42 - 02:44]**

agents that operate in environments, they produce trace data, and what

**[02:44 - 02:46]**

they produce trace data, and what continual learning for agents and

**[02:46 - 02:47]**

continual learning for agents and continual learning for humans basically

**[02:48 - 02:49]**

continual learning for humans basically is is I do a bunch of stuff in the

**[02:49 - 02:52]**

is is I do a bunch of stuff in the world, I think about what I did, and

**[02:52 - 02:54]**

world, I think about what I did, and then I need to update my definition,

**[02:54 - 02:57]**

then I need to update my definition, like my knowledge, stuff I write down,

**[02:57 - 02:58]**

like my knowledge, stuff I write down, in order to respond to the feedback from

**[02:59 - 03:00]**

in order to respond to the feedback from the environment. And if you're continual

**[03:00 - 03:02]**

the environment. And if you're continual learning company, you need traces, and

**[03:02 - 03:04]**

learning company, you need traces, and if you have traces, then you can try to

**[03:04 - 03:09]**

if you have traces, then you can try to do continual learning over your agents.

**[03:11 - 03:13]**

I had to put in a meme because if you look at your data, then you can

**[03:13 - 03:15]**

if you look at your data, then you can be like Will Hunting if anyone's seen

**[03:15 - 03:17]**

be like Will Hunting if anyone's seen the movie, where like everything is

**[03:17 - 03:19]**

the movie, where like everything is super super easy, and you can like

**[03:19 - 03:21]**

super super easy, and you can like improve over time, and I promised Emma I

**[03:21 - 03:23]**

improve over time, and I promised Emma I would put this in there, so putting it

**[03:23 - 03:25]**

would put this in there, so putting it in there.

**[03:25 - 03:29]**

in there. Cool. So, why am I talking a bunch about

**[03:29 - 03:31]**

Cool. So, why am I talking a bunch about traces anyway? So,

**[03:31 - 03:33]**

traces anyway? So, I'm sure a ton of us were software

**[03:33 - 03:34]**

I'm sure a ton of us were software engineers before, we're software

**[03:34 - 03:36]**

engineers before, we're software engineers now, and on the left we have a

**[03:36 - 03:38]**

engineers now, and on the left we have a code block, and we can sort of like read

**[03:38 - 03:40]**

code block, and we can sort of like read the code, and in my head, I can almost

**[03:40 - 03:43]**

the code, and in my head, I can almost reason over what this code does. I can

**[03:43 - 03:45]**

reason over what this code does. I can see the functions, I can see like how

**[03:45 - 03:46]**

see the functions, I can see like how they call each other.

**[03:46 - 03:48]**

they call each other. I can roughly understand the logic in

**[03:48 - 03:52]**

I can roughly understand the logic in Python. Um that doesn't exactly exist in

**[03:52 - 03:55]**

Python. Um that doesn't exactly exist in agent world because agents have prompts,

**[03:55 - 03:56]**

agent world because agents have prompts, they have tools, they have skills, they

**[03:56 - 03:58]**

they have tools, they have skills, they have hooks, they have middlewares, some

**[03:58 - 03:59]**

have hooks, they have middlewares, some agents call other agents and I

**[03:59 - 04:01]**

agents call other agents and I orchestrate them in swarms. It's really

**[04:02 - 04:04]**

orchestrate them in swarms. It's really really hard for humans to reason about

**[04:04 - 04:06]**

really hard for humans to reason about how certain prompts that they change are

**[04:06 - 04:08]**

how certain prompts that they change are actually going to affect agent behavior

**[04:08 - 04:11]**

actually going to affect agent behavior at scale. And this also varies between

**[04:11 - 04:12]**

at scale. And this also varies between the different domains that you're doing

**[04:12 - 04:14]**

the different domains that you're doing it on. So, a prompt change and you're

**[04:14 - 04:16]**

it on. So, a prompt change and you're using for the medical domain is going to

**[04:16 - 04:17]**

using for the medical domain is going to be like completely different than a

**[04:17 - 04:18]**

be like completely different than a prompt change that you want to do for

**[04:18 - 04:19]**

prompt change that you want to do for the law domain.

**[04:19 - 04:22]**

the law domain. And in general, over the last four years

**[04:22 - 04:25]**

And in general, over the last four years since the ChatGPT moment, we've started

**[04:25 - 04:28]**

since the ChatGPT moment, we've started trading determinism for autonomy. And in

**[04:28 - 04:31]**

trading determinism for autonomy. And in that shift, sort of what we need to do

**[04:31 - 04:34]**

that shift, sort of what we need to do is create tools and create systems to

**[04:34 - 04:37]**

is create tools and create systems to still understand agents when they're

**[04:37 - 04:40]**

still understand agents when they're autonomously operating in environments.

**[04:40 - 04:43]**

autonomously operating in environments. So, I talked about traces. Um

**[04:43 - 04:45]**

So, I talked about traces. Um why like why should you read them? And

**[04:45 - 04:48]**

why like why should you read them? And at LangChain, what do we actually do

**[04:48 - 04:50]**

at LangChain, what do we actually do when we're reading traces? So, we

**[04:50 - 04:52]**

when we're reading traces? So, we centralize a bunch of our data, so we

**[04:52 - 04:54]**

centralize a bunch of our data, so we put everything in a tracing project and

**[04:54 - 04:56]**

put everything in a tracing project and this is usually either like per agent or

**[04:56 - 04:57]**

this is usually either like per agent or like centralized across all of our

**[04:57 - 05:01]**

like centralized across all of our agents. And then what we do is we send

**[05:01 - 05:04]**

agents. And then what we do is we send agents to read traces from other agents,

**[05:04 - 05:06]**

agents to read traces from other agents, right? And then we look for a bunch of

**[05:06 - 05:09]**

right? And then we look for a bunch of different things. And we might ask for,

**[05:09 - 05:11]**

different things. And we might ask for, "Hey, like find a bunch of like good and

**[05:11 - 05:13]**

"Hey, like find a bunch of like good and bad interactions where like users got

**[05:13 - 05:14]**

bad interactions where like users got upset or like users are like really

**[05:14 - 05:15]**

upset or like users are like really happy."

**[05:15 - 05:16]**

happy." Um

**[05:16 - 05:18]**

Um another question I might ask is uh this

**[05:18 - 05:20]**

another question I might ask is uh this is a technical question like "Agents now

**[05:20 - 05:22]**

is a technical question like "Agents now run for millions of tokens. Does the

**[05:22 - 05:24]**

run for millions of tokens. Does the agent get really dumb after the first

**[05:24 - 05:27]**

agent get really dumb after the first compaction? After the second compaction?

**[05:27 - 05:28]**

compaction? After the second compaction? Does it never get dumb?" Like how do we

**[05:28 - 05:30]**

Does it never get dumb?" Like how do we actually answer these questions? We need

**[05:30 - 05:31]**

actually answer these questions? We need to do it by actually looking at the

**[05:31 - 05:32]**

to do it by actually looking at the traces.

**[05:32 - 05:34]**

traces. And then the the other thing is like if

**[05:35 - 05:36]**

And then the the other thing is like if I look at the traces, then I can try to

**[05:36 - 05:39]**

I look at the traces, then I can try to prove some counterfactuals, which is

**[05:39 - 05:41]**

prove some counterfactuals, which is "Hey, like I ran GPT 5.5 for this and I

**[05:41 - 05:44]**

"Hey, like I ran GPT 5.5 for this and I heard like GLM is really good. What

**[05:44 - 05:47]**

heard like GLM is really good. What happens if I run GLM 5.2 for this task

**[05:47 - 05:50]**

happens if I run GLM 5.2 for this task and how do I compare them? Metrics,

**[05:50 - 05:52]**

and how do I compare them? Metrics, awesome. The The trace level captures

**[05:52 - 05:54]**

awesome. The The trace level captures the actual like behavior that users see.

**[05:54 - 05:55]**

the actual like behavior that users see. So, that's also like very helpful for

**[05:55 - 05:59]**

So, that's also like very helpful for seeing behavior like fine grain scales.

**[06:03 - 06:04]**

And the way that we sort of think about the data that's being generated by

**[06:04 - 06:06]**

the data that's being generated by agents is that the data that we see

**[06:07 - 06:09]**

agents is that the data that we see today is going to be the smallest that

**[06:09 - 06:11]**

today is going to be the smallest that humans have ever seen in their entire

**[06:11 - 06:14]**

humans have ever seen in their entire lives because we're in this massive

**[06:14 - 06:16]**

lives because we're in this massive exponential shift to our agents are

**[06:16 - 06:18]**

exponential shift to our agents are doing more and more work in the economy.

**[06:18 - 06:19]**

doing more and more work in the economy. And what that means is like the amount

**[06:19 - 06:21]**

And what that means is like the amount of data that humans have produced in our

**[06:21 - 06:24]**

of data that humans have produced in our entire lifetime will soon be eclipsed by

**[06:24 - 06:27]**

entire lifetime will soon be eclipsed by agents running on like year scales and

**[06:27 - 06:29]**

agents running on like year scales and then 6-month scales and 3-month scales

**[06:29 - 06:32]**

then 6-month scales and 3-month scales and then maybe every day, right? Um and

**[06:32 - 06:35]**

and then maybe every day, right? Um and to understand a ton of that data,

**[06:35 - 06:37]**

to understand a ton of that data, roughly what we need to do is contend

**[06:37 - 06:39]**

roughly what we need to do is contend with a couple problems. There's more,

**[06:39 - 06:40]**

with a couple problems. There's more, but these are the two that I'm going to

**[06:40 - 06:42]**

but these are the two that I'm going to focus on. So,

**[06:42 - 06:45]**

focus on. So, one, uh reading traces at scale is super

**[06:45 - 06:47]**

one, uh reading traces at scale is super expensive, uh especially if you have

**[06:47 - 06:49]**

expensive, uh especially if you have millions of traces and if you have

**[06:49 - 06:52]**

millions of traces and if you have millions of tokens per trace, right? Um

**[06:52 - 06:54]**

millions of tokens per trace, right? Um think of it as like an input token cost.

**[06:54 - 06:57]**

think of it as like an input token cost. You can like literally multiply the

**[06:57 - 06:59]**

You can like literally multiply the input token cost uh times the number of

**[06:59 - 07:01]**

input token cost uh times the number of traces times like how big each trace is

**[07:01 - 07:03]**

traces times like how big each trace is on average, right? Um the the other

**[07:03 - 07:05]**

on average, right? Um the the other thing is [clears throat] if I have a

**[07:05 - 07:07]**

thing is [clears throat] if I have a super long interaction with a coding

**[07:07 - 07:08]**

super long interaction with a coding agent like Cloud Code or Codex or like

**[07:08 - 07:10]**

agent like Cloud Code or Codex or like deep agents, um

**[07:10 - 07:12]**

deep agents, um I can't even read that trace with

**[07:12 - 07:15]**

I can't even read that trace with another agent because that that context

**[07:15 - 07:17]**

another agent because that that context like doesn't fit in memory, right? So,

**[07:17 - 07:19]**

like doesn't fit in memory, right? So, it's like we we need to develop systems

**[07:19 - 07:20]**

it's like we we need to develop systems so I can sort of treat that context as

**[07:20 - 07:22]**

so I can sort of treat that context as like an external object and then I can

**[07:22 - 07:24]**

like an external object and then I can sort of query into it, right? So, we we

**[07:24 - 07:26]**

sort of query into it, right? So, we we need to build agents to efficiently mine

**[07:26 - 07:28]**

need to build agents to efficiently mine data from other agents and it's it's no

**[07:28 - 07:30]**

data from other agents and it's it's no longer as simple as just like feeding

**[07:30 - 07:32]**

longer as simple as just like feeding the data into context and there's like

**[07:32 - 07:34]**

the data into context and there's like tricks that we'll sort of talk about uh

**[07:34 - 07:36]**

tricks that we'll sort of talk about uh to to do that well.

**[07:36 - 07:39]**

to to do that well. Great. So, one of the things that I

**[07:39 - 07:40]**

Great. So, one of the things that I think is really really cool in the last

**[07:40 - 07:43]**

think is really really cool in the last 6 months is that open models have

**[07:43 - 07:45]**

6 months is that open models have basically hit an inflection point in

**[07:45 - 07:48]**

basically hit an inflection point in intelligence that we at LangChain don't

**[07:48 - 07:50]**

intelligence that we at LangChain don't reach for the frontier models for every

**[07:50 - 07:53]**

reach for the frontier models for every single use case. We're quite conscious

**[07:53 - 07:55]**

single use case. We're quite conscious about what is the minimum level of

**[07:55 - 07:57]**

about what is the minimum level of intelligence that I need to do any given

**[07:57 - 08:00]**

intelligence that I need to do any given task. And like practically speaking,

**[08:00 - 08:02]**

task. And like practically speaking, honestly, yes, we start with Opus, we

**[08:02 - 08:04]**

honestly, yes, we start with Opus, we start with 55 because we just want to

**[08:04 - 08:06]**

start with 55 because we just want to know if the task is even possible. But

**[08:06 - 08:09]**

know if the task is even possible. But then once we reach that sort of like

**[08:09 - 08:11]**

then once we reach that sort of like waterline, then we like look back at

**[08:11 - 08:13]**

waterline, then we like look back at those traces and we see, "Hey, can we

**[08:13 - 08:15]**

those traces and we see, "Hey, can we use an open model to do the same thing?"

**[08:15 - 08:16]**

use an open model to do the same thing?" So, this is a bunch of work that we did

**[08:17 - 08:19]**

So, this is a bunch of work that we did with Harvey and then their lab legal

**[08:19 - 08:21]**

with Harvey and then their lab legal benchmark. Basically, what we're looking

**[08:21 - 08:22]**

benchmark. Basically, what we're looking at is

**[08:22 - 08:25]**

at is can I match the trace judging capability

**[08:25 - 08:28]**

can I match the trace judging capability of Opus with an open cheaper model? And

**[08:28 - 08:32]**

of Opus with an open cheaper model? And the answer is roughly yes at like an

**[08:32 - 08:34]**

the answer is roughly yes at like an order or like two orders of magnitude

**[08:34 - 08:36]**

order or like two orders of magnitude cheaper. And like the way we do that is

**[08:36 - 08:38]**

cheaper. And like the way we do that is we try a bunch of models,

**[08:38 - 08:38]**

we try a bunch of models, we do a bunch of like harness

**[08:38 - 08:40]**

we do a bunch of like harness engineering, and the harness engineering

**[08:40 - 08:42]**

engineering, and the harness engineering is informed by a bunch of the traces

**[08:42 - 08:44]**

is informed by a bunch of the traces that we read. So, it's like, "Hey, like

**[08:44 - 08:46]**

that we read. So, it's like, "Hey, like Opus reasons about things in this way.

**[08:46 - 08:48]**

Opus reasons about things in this way. Maybe that's because of the prompt.

**[08:48 - 08:49]**

Maybe that's because of the prompt. Maybe Opus is just smarter, which it is,

**[08:49 - 08:51]**

Maybe Opus is just smarter, which it is, than a bunch of the open models, but

**[08:51 - 08:52]**

than a bunch of the open models, but that might mean I need to give it a

**[08:52 - 08:54]**

that might mean I need to give it a little bit more guidance so it can reach

**[08:54 - 08:55]**

little bit more guidance so it can reach the sort of same intelligence level at

**[08:55 - 08:56]**

the sort of same intelligence level at like a much

**[08:56 - 08:58]**

like a much much lower cost."

**[08:58 - 09:00]**

much lower cost." And the the other thing that we sort of

**[09:00 - 09:03]**

And the the other thing that we sort of look at is like harness engineering is

**[09:03 - 09:04]**

look at is like harness engineering is amazing.

**[09:04 - 09:06]**

amazing. You get instant feedback and you can

**[09:06 - 09:08]**

You get instant feedback and you can sort of like run on your evals, but

**[09:08 - 09:10]**

sort of like run on your evals, but eventually what we find is you hit a

**[09:10 - 09:12]**

eventually what we find is you hit a threshold of intelligence where it's

**[09:12 - 09:15]**

threshold of intelligence where it's like "If I keep tweaking this prompt,

**[09:15 - 09:16]**

like "If I keep tweaking this prompt, I'm not going to get too much more out

**[09:16 - 09:18]**

I'm not going to get too much more out of it." And once we reach that point, we

**[09:18 - 09:20]**

of it." And once we reach that point, we sort of look at, "Okay, can I actually

**[09:20 - 09:23]**

sort of look at, "Okay, can I actually like fine-tune the model on my

**[09:23 - 09:25]**

like fine-tune the model on my domain-specific task?" And can I like

**[09:25 - 09:27]**

domain-specific task?" And can I like make it better on those tasks? And what

**[09:27 - 09:29]**

make it better on those tasks? And what we find is if we take like base models

**[09:29 - 09:32]**

we find is if we take like base models and we tune them on like very specific

**[09:32 - 09:33]**

and we tune them on like very specific vertical tasks, which is what a lot of

**[09:33 - 09:35]**

vertical tasks, which is what a lot of our customers do, they don't really care

**[09:35 - 09:37]**

our customers do, they don't really care about the entire variance of tasks. like

**[09:37 - 09:39]**

about the entire variance of tasks. like they care about what their customers

**[09:39 - 09:40]**

they care about what their customers care about. So, if we focus on that

**[09:40 - 09:42]**

care about. So, if we focus on that narrow set of tasks, then we can

**[09:42 - 09:44]**

narrow set of tasks, then we can fine-tune base models to sort of like

**[09:44 - 09:47]**

fine-tune base models to sort of like reach and then also go beyond frontier

**[09:47 - 09:48]**

reach and then also go beyond frontier performance. And I think one sort of

**[09:48 - 09:51]**

performance. And I think one sort of like small thing I'll mention as a lot

**[09:51 - 09:53]**

like small thing I'll mention as a lot of people are getting into fine-tuning

**[09:53 - 09:55]**

of people are getting into fine-tuning is that another sort of like economic

**[09:55 - 09:58]**

is that another sort of like economic decision is that you can move from token

**[09:58 - 10:02]**

decision is that you can move from token costs to hardware costs. And this is

**[10:02 - 10:04]**

costs to hardware costs. And this is like can be a really big change, right?

**[10:04 - 10:06]**

like can be a really big change, right? Cuz like you're very used to hey, like a

**[10:06 - 10:08]**

Cuz like you're very used to hey, like a million tokens cost this much, not as

**[10:08 - 10:09]**

million tokens cost this much, not as much like this cluster sort of costs

**[10:09 - 10:12]**

much like this cluster sort of costs this much. But for like very high

**[10:12 - 10:14]**

this much. But for like very high inference workloads, we find it to be

**[10:14 - 10:16]**

inference workloads, we find it to be way cheaper just to like run a cluster

**[10:16 - 10:17]**

way cheaper just to like run a cluster and I get like unlimited inference on

**[10:18 - 10:19]**

and I get like unlimited inference on that cluster. I don't have to worry

**[10:19 - 10:20]**

that cluster. I don't have to worry about tokens, but I can just do the

**[10:20 - 10:22]**

about tokens, but I can just do the calculation of like, hey,

**[10:22 - 10:23]**

calculation of like, hey, um this will end up being cheaper and

**[10:23 - 10:25]**

um this will end up being cheaper and then I can spin it down when I don't

**[10:25 - 10:27]**

then I can spin it down when I don't need it.

**[10:30 - 10:31]**

Cool. And I said all of this um so we obviously like built a product to

**[10:31 - 10:33]**

so we obviously like built a product to do that. Uh I won't shill it too much,

**[10:33 - 10:36]**

do that. Uh I won't shill it too much, but it's LangSplat engine. Uh basically,

**[10:36 - 10:39]**

but it's LangSplat engine. Uh basically, this product is trying to automate this

**[10:39 - 10:42]**

this product is trying to automate this loop for you, which is if you have any

**[10:42 - 10:44]**

loop for you, which is if you have any volume of trace data and you're looking

**[10:44 - 10:46]**

volume of trace data and you're looking for something that trace data or you

**[10:46 - 10:47]**

for something that trace data or you want to generate e-vals from that trace

**[10:47 - 10:50]**

want to generate e-vals from that trace data or you want to like generate

**[10:50 - 10:51]**

data or you want to like generate feedback for like humans to read from

**[10:52 - 10:53]**

feedback for like humans to read from that trace data, it will go read all of

**[10:53 - 10:55]**

that trace data, it will go read all of it, it'll like find issues, it'll

**[10:55 - 10:56]**

it, it'll like find issues, it'll agentically search over it, and they can

**[10:56 - 10:59]**

agentically search over it, and they can like prepare data sets for you to do

**[10:59 - 11:02]**

like prepare data sets for you to do something after. And a bit of a leader,

**[11:02 - 11:03]**

something after. And a bit of a leader, um

**[11:03 - 11:05]**

um what that something basically is is the

**[11:05 - 11:08]**

what that something basically is is the outputs of this trace mining exercise.

**[11:08 - 11:08]**

outputs of this trace mining exercise. So,

**[11:09 - 11:10]**

So, there's like three things that I

**[11:10 - 11:12]**

there's like three things that I mentioned here uh which we see a bunch

**[11:12 - 11:14]**

mentioned here uh which we see a bunch and we kind of put into the product. So,

**[11:14 - 11:17]**

and we kind of put into the product. So, one is distillation and fine-tuning,

**[11:17 - 11:20]**

one is distillation and fine-tuning, which is let's say I'm running GLM 5.2.

**[11:20 - 11:23]**

which is let's say I'm running GLM 5.2. It's doing great, but I think that I can

**[11:23 - 11:25]**

It's doing great, but I think that I can run this task like way cheaper with like

**[11:25 - 11:27]**

run this task like way cheaper with like a 9B or 13B model. Then what I'll do is

**[11:27 - 11:29]**

a 9B or 13B model. Then what I'll do is like I'll take the good traces and the

**[11:29 - 11:32]**

like I'll take the good traces and the good examples from the GLM 5.2 runs,

**[11:32 - 11:33]**

good examples from the GLM 5.2 runs, I'll prepare them in a data set, and

**[11:33 - 11:35]**

I'll prepare them in a data set, and then I'll try to fine-tune a small model

**[11:35 - 11:37]**

then I'll try to fine-tune a small model on that data set to like mimic behavior,

**[11:37 - 11:39]**

on that data set to like mimic behavior, essentially, right? And this is like

**[11:39 - 11:43]**

essentially, right? And this is like distillation, SFT. The The other one is

**[11:43 - 11:45]**

distillation, SFT. The The other one is generating evals and environments. So,

**[11:45 - 11:48]**

generating evals and environments. So, maybe another slightly hot take, I think

**[11:48 - 11:51]**

maybe another slightly hot take, I think you can basically define agent behavior

**[11:51 - 11:53]**

you can basically define agent behavior by showing the evals that you ran on it,

**[11:53 - 11:55]**

by showing the evals that you ran on it, right? Like, if someone showed me all

**[11:55 - 11:56]**

right? Like, if someone showed me all the things that they're trying to test

**[11:56 - 11:58]**

the things that they're trying to test their agent on, I think I would have a

**[11:58 - 12:00]**

their agent on, I think I would have a rough idea about how that agent is going

**[12:00 - 12:02]**

rough idea about how that agent is going to behave because it literally like hill

**[12:02 - 12:05]**

to behave because it literally like hill climbs those evals, and you you alter

**[12:05 - 12:07]**

climbs those evals, and you you alter the behavior of the agent to make the

**[12:07 - 12:09]**

the behavior of the agent to make the evals pass, right? Like, the purpose of

**[12:09 - 12:11]**

evals pass, right? Like, the purpose of evals is roughly to try to make them

**[12:11 - 12:13]**

evals is roughly to try to make them pass, right? So, I update my agent so

**[12:13 - 12:15]**

pass, right? So, I update my agent so that they essentially pass. And then the

**[12:15 - 12:17]**

that they essentially pass. And then the the other thing is um like humans are

**[12:17 - 12:20]**

the other thing is um like humans are still in the loop. Like, I need to know

**[12:20 - 12:23]**

still in the loop. Like, I need to know that customers are happy. I also want to

**[12:23 - 12:24]**

that customers are happy. I also want to know what my agents are doing. I just

**[12:24 - 12:26]**

know what my agents are doing. I just don't have the bandwidth to read a bunch

**[12:26 - 12:29]**

don't have the bandwidth to read a bunch of traces. So, preparing content for

**[12:29 - 12:31]**

of traces. So, preparing content for humans is still like really, really

**[12:31 - 12:34]**

humans is still like really, really valuable today, especially in like

**[12:34 - 12:36]**

valuable today, especially in like high-trust domains like legal and

**[12:36 - 12:38]**

high-trust domains like legal and medical. Like, some human needs to

**[12:38 - 12:40]**

medical. Like, some human needs to review this, um but they can't read it

**[12:40 - 12:42]**

review this, um but they can't read it all, so we try to make it easy for them

**[12:42 - 12:46]**

all, so we try to make it easy for them to process all that data.

**[12:47 - 12:50]**

Great. This is um maybe a bit of a throwback. Like, how many people here

**[12:50 - 12:52]**

throwback. Like, how many people here know what like scikit-learn is? Uh maybe

**[12:52 - 12:53]**

know what like scikit-learn is? Uh maybe put your uh psych This crowd is just

**[12:53 - 12:57]**

put your uh psych This crowd is just awesome. Um cool. So, uh when I was like

**[12:57 - 12:59]**

awesome. Um cool. So, uh when I was like first doing my PhD, uh

**[12:59 - 13:01]**

first doing my PhD, uh my PhD was like kind of trying to do

**[13:01 - 13:04]**

my PhD was like kind of trying to do this, but like add new algorithms to

**[13:04 - 13:05]**

this, but like add new algorithms to scikit-learn. And like, what

**[13:05 - 13:09]**

scikit-learn. And like, what scikit-learn basically is uh an abstract

**[13:09 - 13:13]**

scikit-learn basically is uh an abstract level, it's a bunch of helpers to fit

**[13:13 - 13:15]**

level, it's a bunch of helpers to fit learning systems to data, right? And

**[13:15 - 13:17]**

learning systems to data, right? And like, classical machine learning, I had

**[13:17 - 13:18]**

like, classical machine learning, I had like a data set, I tried to fit it to

**[13:18 - 13:21]**

like a data set, I tried to fit it to it, but I think the same principles that

**[13:21 - 13:24]**

it, but I think the same principles that we use in modern in I got I call it

**[13:24 - 13:25]**

we use in modern in I got I call it classical machine learning, it's like 6

**[13:25 - 13:27]**

classical machine learning, it's like 6 years ago. Um that we do in classical

**[13:27 - 13:29]**

years ago. Um that we do in classical machine learning uh definitely still

**[13:29 - 13:32]**

machine learning uh definitely still apply to this agent-first world. Um,

**[13:32 - 13:34]**

apply to this agent-first world. Um, the way that they apply is what I like

**[13:34 - 13:38]**

the way that they apply is what I like to call model harness task fit. So, we

**[13:38 - 13:40]**

to call model harness task fit. So, we still have this sort of like fit

**[13:40 - 13:43]**

still have this sort of like fit function that I'm going to try to like

**[13:43 - 13:46]**

function that I'm going to try to like take my data, take a harness, take a

**[13:46 - 13:47]**

take my data, take a harness, take a model, and I'm going to try to fit it

**[13:47 - 13:49]**

model, and I'm going to try to fit it all together to make sure that all of my

**[13:49 - 13:52]**

all together to make sure that all of my tasks pass, right? The algorithms look

**[13:52 - 13:56]**

tasks pass, right? The algorithms look slightly different, uh but the overall

**[13:56 - 13:58]**

slightly different, uh but the overall process of machine learning doesn't

**[13:58 - 14:00]**

process of machine learning doesn't really look that different, and we'll

**[14:00 - 14:03]**

really look that different, and we'll talk about maybe roughly what our job

**[14:03 - 14:06]**

talk about maybe roughly what our job becomes in this data-first, agent-first,

**[14:06 - 14:08]**

becomes in this data-first, agent-first, fit-first world. So, a couple of our

**[14:08 - 14:11]**

fit-first world. So, a couple of our main jobs now are

**[14:11 - 14:13]**

main jobs now are find good fit functions. So, these are

**[14:13 - 14:15]**

find good fit functions. So, these are like auto research. This is tons of

**[14:15 - 14:17]**

like auto research. This is tons of great work that's being done in RL on

**[14:17 - 14:20]**

great work that's being done in RL on different methods like OPD, OPSD,

**[14:20 - 14:22]**

different methods like OPD, OPSD, trySFT.

**[14:22 - 14:24]**

trySFT. And also find good data, right? So, if

**[14:24 - 14:26]**

And also find good data, right? So, if you put those two things together, then

**[14:26 - 14:28]**

you put those two things together, then that is basically the applied or just

**[14:28 - 14:30]**

that is basically the applied or just overall research question that every

**[14:30 - 14:33]**

overall research question that every team has to make their agents better.

**[14:33 - 14:35]**

team has to make their agents better. I like some some examples that we've

**[14:35 - 14:37]**

I like some some examples that we've seen that are like very popular that

**[14:37 - 14:39]**

seen that are like very popular that we're pretty bullish on are just

**[14:39 - 14:41]**

we're pretty bullish on are just generally auto research. So, if you have

**[14:41 - 14:43]**

generally auto research. So, if you have some sort of score that you can make

**[14:43 - 14:45]**

some sort of score that you can make number go up, uh

**[14:45 - 14:47]**

number go up, uh agents are pretty good at making that

**[14:47 - 14:48]**

agents are pretty good at making that number go up. They might cheat a little

**[14:48 - 14:49]**

number go up. They might cheat a little bit and you need to like check them on

**[14:49 - 14:51]**

bit and you need to like check them on some stuff. Um, but this sort of like

**[14:51 - 14:54]**

some stuff. Um, but this sort of like general feedback loop of do something,

**[14:54 - 14:56]**

general feedback loop of do something, read the results, read the traces, and

**[14:56 - 14:58]**

read the results, read the traces, and then do an update ends up being pretty

**[14:58 - 15:00]**

then do an update ends up being pretty useful. And then I talked about like

**[15:00 - 15:02]**

useful. And then I talked about like model fine-tuning a bunch as well.

**[15:02 - 15:03]**

model fine-tuning a bunch as well. Um,

**[15:03 - 15:05]**

Um, so we we just like went and did this. Uh

**[15:05 - 15:07]**

so we we just like went and did this. Uh this was I think even before the term

**[15:07 - 15:08]**

this was I think even before the term auto research came out, but a lot of

**[15:08 - 15:10]**

auto research came out, but a lot of people were doing it, which is hey, like

**[15:10 - 15:12]**

people were doing it, which is hey, like terminal benches like really hard. Uh

**[15:12 - 15:14]**

terminal benches like really hard. Uh what would happen if an agent just like

**[15:14 - 15:17]**

what would happen if an agent just like read its traces, uh proposed

**[15:17 - 15:19]**

read its traces, uh proposed experiments, and then tried to do fixes?

**[15:19 - 15:21]**

experiments, and then tried to do fixes? Um, I think one like really key thing

**[15:21 - 15:23]**

Um, I think one like really key thing here is uh

**[15:23 - 15:26]**

here is uh giving agents dense feedback signals.

**[15:26 - 15:28]**

giving agents dense feedback signals. So, like terminal bench, the output is

**[15:28 - 15:30]**

So, like terminal bench, the output is just a number, right? Like, did you pass

**[15:30 - 15:32]**

just a number, right? Like, did you pass or did you not pass? Uh that's like kind

**[15:32 - 15:33]**

or did you not pass? Uh that's like kind of helpful, but if I give you like a

**[15:33 - 15:35]**

of helpful, but if I give you like a super random task, like you just did a

**[15:35 - 15:37]**

super random task, like you just did a bunch of stuff, and then I just said

**[15:37 - 15:39]**

bunch of stuff, and then I just said like you failed or you passed, uh if you

**[15:39 - 15:40]**

like you failed or you passed, uh if you failed, like you wouldn't really have a

**[15:40 - 15:42]**

failed, like you wouldn't really have a good signal to figure out what you

**[15:42 - 15:45]**

good signal to figure out what you should do next, right? So, densifying

**[15:45 - 15:47]**

should do next, right? So, densifying feedback is uh really good way to

**[15:47 - 15:49]**

feedback is uh really good way to improve agents, and like traces are the

**[15:49 - 15:51]**

improve agents, and like traces are the substrate that hold that feedback. And

**[15:51 - 15:52]**

substrate that hold that feedback. And then agents are very good at like

**[15:53 - 15:54]**

then agents are very good at like reading those uh those traces and then

**[15:54 - 15:58]**

reading those uh those traces and then figuring out like what to do next. Um

**[15:58 - 16:01]**

figuring out like what to do next. Um and then this sort of question always

**[16:01 - 16:03]**

and then this sort of question always comes up, which is

**[16:03 - 16:05]**

comes up, which is when should I like harness Enge? When

**[16:05 - 16:07]**

when should I like harness Enge? When should I fine-tune? Uh should I do more

**[16:07 - 16:10]**

should I fine-tune? Uh should I do more harness Enge after it? I'm like pretty

**[16:10 - 16:13]**

harness Enge after it? I'm like pretty bullish on the idea of if you need to do

**[16:13 - 16:16]**

bullish on the idea of if you need to do something for improving your agent, the

**[16:16 - 16:18]**

something for improving your agent, the best thing that you can do is collect

**[16:18 - 16:20]**

best thing that you can do is collect feedback as quickly as possible, like

**[16:20 - 16:22]**

feedback as quickly as possible, like either from humans labeling or just

**[16:22 - 16:24]**

either from humans labeling or just letting the agents run. So, like harness

**[16:24 - 16:26]**

letting the agents run. So, like harness engineering gives you feedback in maybe

**[16:26 - 16:27]**

engineering gives you feedback in maybe 2 minutes. Um

**[16:27 - 16:29]**

2 minutes. Um once you sort of saturate the harness

**[16:29 - 16:32]**

once you sort of saturate the harness engineering ceiling, right? Then you can

**[16:32 - 16:34]**

engineering ceiling, right? Then you can maybe try to do like fine-tuning after

**[16:34 - 16:36]**

maybe try to do like fine-tuning after that, but we find a lot of teams are

**[16:36 - 16:38]**

that, but we find a lot of teams are happy with harness engineering and uh it

**[16:38 - 16:40]**

happy with harness engineering and uh it solves their customer use case, so like

**[16:40 - 16:41]**

solves their customer use case, so like we always sort of sort of recommend it.

**[16:41 - 16:42]**

we always sort of sort of recommend it. And then we have this like sort of

**[16:42 - 16:44]**

And then we have this like sort of sandwich, which is like try harness

**[16:44 - 16:46]**

sandwich, which is like try harness engineering, try to do fine-tuning to

**[16:46 - 16:47]**

engineering, try to do fine-tuning to sort of like break through that ceiling,

**[16:47 - 16:49]**

sort of like break through that ceiling, and then do more harness engineering

**[16:49 - 16:51]**

and then do more harness engineering again if you need to.

**[16:51 - 16:54]**

again if you need to. And then I'll sort of end on the the

**[16:54 - 16:57]**

And then I'll sort of end on the the idea generally of continual learning is

**[16:57 - 16:59]**

idea generally of continual learning is that there's an agent taking actions in

**[16:59 - 17:02]**

that there's an agent taking actions in the environment, and then it needs to

**[17:02 - 17:06]**

the environment, and then it needs to use that information, sorry guys, needs

**[17:06 - 17:09]**

use that information, sorry guys, needs to use that information to update

**[17:09 - 17:11]**

to use that information to update information about itself, right? So,

**[17:11 - 17:13]**

information about itself, right? So, it's like I did a bunch of these tasks,

**[17:13 - 17:15]**

it's like I did a bunch of these tasks, and like I need to update my prompts to

**[17:15 - 17:17]**

and like I need to update my prompts to make sure I do them more efficiently. Or

**[17:17 - 17:21]**

make sure I do them more efficiently. Or users are users keep asking to search

**[17:21 - 17:23]**

users are users keep asking to search for these types of things, I should

**[17:23 - 17:26]**

for these types of things, I should maybe tell like tell my creator that

**[17:26 - 17:27]**

maybe tell like tell my creator that like they're they're doing this sort of

**[17:27 - 17:29]**

like they're they're doing this sort of stuff, right? It's like taking action in

**[17:29 - 17:30]**

stuff, right? It's like taking action in the environment kind of like humans do

**[17:30 - 17:33]**

the environment kind of like humans do and updating ourselves. What that looks

**[17:33 - 17:36]**

and updating ourselves. What that looks like today, slightly unclear, but we

**[17:36 - 17:38]**

like today, slightly unclear, but we think that you're going to have to do it

**[17:38 - 17:40]**

think that you're going to have to do it across all three axes, which is one,

**[17:40 - 17:42]**

across all three axes, which is one, collect a bunch of training data, which

**[17:42 - 17:45]**

collect a bunch of training data, which is like observational data from agents

**[17:45 - 17:46]**

is like observational data from agents taking actions. The The other one is

**[17:46 - 17:49]**

taking actions. The The other one is like harness updates generally, like

**[17:49 - 17:50]**

like harness updates generally, like you know, the the Codex harness and the

**[17:51 - 17:52]**

you know, the the Codex harness and the Cloud Code harness and like our harness

**[17:52 - 17:54]**

Cloud Code harness and like our harness and everyone's harness, like they look a

**[17:54 - 17:56]**

and everyone's harness, like they look a certain way because like models are are

**[17:56 - 17:57]**

certain way because like models are are trained in them and they look a certain

**[17:57 - 17:59]**

trained in them and they look a certain way because of the tasks that they do in

**[17:59 - 18:01]**

way because of the tasks that they do in the real world and we think like

**[18:01 - 18:03]**

the real world and we think like evolving those over time is going to be

**[18:03 - 18:06]**

evolving those over time is going to be super important in in order to make them

**[18:06 - 18:08]**

super important in in order to make them work. And

**[18:08 - 18:10]**

work. And the the last thing is like memory. So,

**[18:10 - 18:11]**

the the last thing is like memory. So, uh

**[18:11 - 18:13]**

uh we humans are like really good at like

**[18:13 - 18:15]**

we humans are like really good at like remembering stuff over time, but we are

**[18:15 - 18:18]**

remembering stuff over time, but we are not append-only logs of information. And

**[18:18 - 18:19]**

not append-only logs of information. And if agents are going to be working with

**[18:19 - 18:22]**

if agents are going to be working with us over like year, 5-year, decade,

**[18:22 - 18:24]**

us over like year, 5-year, decade, lifetime time scales, we cannot just

**[18:24 - 18:26]**

lifetime time scales, we cannot just append everything to like a really big

**[18:26 - 18:28]**

append everything to like a really big file and then search over it. There's a

**[18:28 - 18:30]**

file and then search over it. There's a ton of stuff that needs to happen with

**[18:30 - 18:32]**

ton of stuff that needs to happen with like updating those files over time and

**[18:32 - 18:33]**

like updating those files over time and then just making memory like really

**[18:33 - 18:35]**

then just making memory like really efficient. But, we think a lot of that

**[18:35 - 18:38]**

efficient. But, we think a lot of that actually comes from this idea of scaling

**[18:38 - 18:40]**

actually comes from this idea of scaling sleep time compute and and dreaming

**[18:40 - 18:41]**

sleep time compute and and dreaming generally. So, it's like read all of the

**[18:41 - 18:44]**

generally. So, it's like read all of the traces over the entire agent life cycle

**[18:44 - 18:46]**

traces over the entire agent life cycle and then like do [music] things to

**[18:46 - 18:49]**

and then like do [music] things to update agent state.

**[18:49 - 18:51]**

update agent state. Awesome. So, like quick quick takeaways,

**[18:51 - 18:54]**

Awesome. So, like quick quick takeaways, uh mining traces gives you signals to

**[18:54 - 18:56]**

uh mining traces gives you signals to hill climb on. Uh I would say like if

**[18:56 - 18:58]**

hill climb on. Uh I would say like if you have an agent, just turn on tracing

**[18:58 - 19:00]**

you have an agent, just turn on tracing and point an agent at it and that's like

**[19:00 - 19:02]**

and point an agent at it and that's like the easiest thing that you can do to see

**[19:02 - 19:04]**

the easiest thing that you can do to see like to basically understand what your

**[19:04 - 19:05]**

like to basically understand what your agents are doing.

**[19:06 - 19:08]**

agents are doing. Uh we're very excited about open models.

**[19:08 - 19:09]**

Uh we're very excited about open models. We want to help you fine-tune open

**[19:09 - 19:12]**

We want to help you fine-tune open models. Um we provide them as a service

**[19:12 - 19:13]**

models. Um we provide them as a service as well. So, if you're interested in

**[19:13 - 19:14]**

as well. So, if you're interested in that, would would love to chat how you

**[19:15 - 19:17]**

that, would would love to chat how you can use open models to make everything

**[19:17 - 19:19]**

can use open models to make everything smarter and cheaper. Um,

**[19:19 - 19:20]**

smarter and cheaper. Um, continual learning is about operating

**[19:20 - 19:22]**

continual learning is about operating environments and then integrating that

**[19:22 - 19:24]**

environments and then integrating that data back into agent state. And then

**[19:25 - 19:27]**

data back into agent state. And then finally, I think this is so cool that

**[19:27 - 19:28]**

finally, I think this is so cool that like we have systems that's going to

**[19:28 - 19:30]**

like we have systems that's going to pre- that are going to produce more data

**[19:30 - 19:31]**

pre- that are going to produce more data than we ever have before.

**[19:31 - 19:34]**

than we ever have before. Uh, we need to all come up with like

**[19:34 - 19:36]**

Uh, we need to all come up with like interesting research directions to learn

**[19:36 - 19:37]**

interesting research directions to learn how to like manage that at scale and

**[19:37 - 19:39]**

how to like manage that at scale and like make all of our agents better.

**[19:39 - 19:40]**

like make all of our agents better. And with that,

**[19:40 - 19:42]**

And with that, thank you. Thank you all for coming.

**[19:42 - 19:58]**

thank you. Thank you all for coming. >> [applause]
