// Reference only: use an already-authorized EIP-1193 wallet on Stable Studionet.
// Run ONE step, wait for FINALIZED / MAJORITY_AGREE and successful execution,
// then read get_book from latest finalized state before choosing the next revision.
import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import {TransactionHashVariant} from 'genlayer-js/types';
export function calls(wallet, account, address) {
  const client=createClient({chain:studionet,account,provider:wallet});
  const read=bookId=>client.readContract({address,functionName:'get_book',args:[bookId],transactionHashVariant:TransactionHashVariant.LATEST_FINAL});
  const write=async(functionName,args)=>{
    if(await client.getChainId()!==61999)throw Error('Wrong chain');
    if(BigInt(await client.request({method:'eth_gasPrice',params:[]}))!==0n)throw Error('Nonzero cost');
    return client.writeContract({address,functionName,args,value:0n,leaderOnly:false});
  };
  return {
    create:()=>write('create',['my-packs','AA-1 identical brass clips',JSON.stringify(['case','box','piece'])]),
    link:(id,currentRevision,from,to,statement)=>write('link',[id,currentRevision,from,to,statement]),
    freeze:(id,currentRevision)=>write('freeze',[id,currentRevision]),
    read,
    convert:(id,from,to,amount)=>client.readContract({address,functionName:'convert',args:[id,from,to,amount],transactionHashVariant:TransactionHashVariant.LATEST_FINAL})
  };
}
