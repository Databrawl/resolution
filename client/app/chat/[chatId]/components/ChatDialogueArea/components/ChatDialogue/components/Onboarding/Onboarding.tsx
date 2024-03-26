import {MessageRow} from "../QADisplay";


export const Onboarding = (): JSX.Element => {
    const greeting = `
Welcome! 👋

I'm **REsolution AI** but feel free to call me Reso. I am the first autonomous customer support team with multiple AI agents under the hood.

This first demo showcases my conversational abilities as your customer support agent. 

I trained on publicly available data that my creators found about Crypto.com. And the more I learn, the more valuable I become to both your customers and your team.

### **Why you should hire me**

- I can cover you 24/7 on communication with your customers with over 70% resolution rate.
- I'm capable of multitasking and can handle any volume of requests with ease.
- I maintain stability, exhibit high empathy, and have flawless memory.
- I'm proactive, constantly seeking to expand my knowledge and learn.
- Plus, I'm 10x cost-effective than the typical human customer support agent and could save plenty of hours for your team.

I deal with these customers' inquiries:
1. **Any product-related questions.** 
   If I encounter gaps in my knowledge about the product, I will reach out to you for additional details that you can directly provide to me, similar to interacting with a human.
2. **Resolving any issues customers face.**
   If I can't resolve an issue after several attempts, I'll gather the necessary details about the issue and the customers’ email to follow up them later.
3. **Collecting feedback on your product.**
   If a customer wishes to share valuable feedback, I'll immediately take it on board, clarifying details, and highlighting it for your team — ensuring it doesn't go unnoticed.

Let's chat about your product as if you were the customer 😉
    `;

    return (
        <div className="flex flex-col gap-2 mb-3">
            <MessageRow speaker={"assistant"} brainName={"Quivr"} text={greeting}/>
        </div>
    );
};
