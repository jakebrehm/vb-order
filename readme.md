A script meant to help automate our weekly lunch order at a restaurant named *Village Burger*.

# What does it do?

Previously, those that wanted to go would enter their order into a shared spreadsheet (shown below), and someone would call in the order so that it can be ready by the time we get to the restaurant. However, the person that is calling in the order would have to manually divide the orders by payment type, cook, etc., which can be slightly annoying when you don't have much time that day. A pivot table can mostly accomplish this, except it is unable to show the notes that someone may have added to his/her order.

<p align="center">
  <img src="https://github.com/jakebrehm/vb-order/blob/master/img/spreadsheet.png" alt="Spreadsheet example"/>
</p>

Because of this, I decided to write a script that would do this automatically and then email a summary of all of the orders (including notes) to whoever's going to call it in that week. An example of the summary email is shown below.

```
From a total of 10 order(s), 7 will be paid with credit, 2 will be paid with cash, and 1 did not specify a payment method.

CREDIT:
(2) BOW: MW
	[Jake] Test
	[Austin] Hold the spit
(1) BOW w/ Dead Egg: MW
(1) BOW: MR
(2) Turkey Club
(1) Villy Steak and Cheese Sub

CASH:
(2) BOW: MR
	[Mary Kate] Another one

UNSPECIFIED:
(1) Spitfire: MR
```

It's a relatively simple script, but it just showcases how useful programming languages can be.

# Authors
- **Jake Brehm** - *Initial Work* - [Email](mailto:mail@jakebrehm.com) | [Github](http://github.com/jakebrehm) | [LinkedIn](http://linkedin.com/in/jacobbrehm)