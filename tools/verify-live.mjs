// Read-only verification. No account, signer, submission, deployment or appeal.
import {createClient,abi} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import {TransactionHashVariant} from 'genlayer-js/types';
import fs from 'node:fs';
import crypto from 'node:crypto';
const root=new URL('../',import.meta.url);
const load=p=>JSON.parse(fs.readFileSync(new URL(p,root),'utf8'));
const need=(condition,message)=>{if(!condition)throw Error(message);};
const clean=v=>v instanceof Map?Object.fromEntries([...v].map(([k,x])=>[k,clean(x)])):typeof v==='bigint'?Number(v):Array.isArray(v)?v.map(clean):v&&typeof v==='object'?Object.fromEntries(Object.entries(v).map(([k,x])=>[k,clean(x)])):v;
const canonical=v=>Array.isArray(v)?'['+v.map(canonical).join(',')+']':v&&typeof v==='object'?'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}':JSON.stringify(v);
const hash=v=>crypto.createHash('sha256').update(canonical(v)).digest('hex');
const equal=(a,b)=>canonical(a)===canonical(b);
const manifest=load('deployment.json');const fixture=load('examples/clips.json');
const client=createClient({chain:studionet});
need(await client.getChainId()===61999,'CHAIN_MISMATCH');
const source=await client.getContractCode(manifest.address);
need(source===fs.readFileSync(new URL('contracts/ratio_rail.py',root),'utf8'),'SOURCE_BYTES_MISMATCH');
need(crypto.createHash('sha256').update(source).digest('hex')===manifest.source_sha256,'SOURCE_HASH_MISMATCH');
const protocol=JSON.parse(await client.readContract({address:manifest.address,functionName:'protocol',args:[],transactionHashVariant:TransactionHashVariant.LATEST_FINAL}));
need(protocol.version==='ratiorail-1','PROTOCOL_MISMATCH');
for(const [step,txHash] of Object.entries(manifest.transactions)){
  const tx=await client.getTransaction({hash:txHash});
  need(tx.statusName==='FINALIZED'&&tx.result_name==='MAJORITY_AGREE',step+':NO_FINAL_AGREEMENT');
  need(tx.consensus_data?.leader_receipt?.find(r=>r.mode==='leader')?.result?.status==='return',step+':EXECUTION_FAILED');
  need(tx.leader_only===false&&tx.execution_mode==='NORMAL'&&tx.appealed===false,step+':CONSENSUS_MODE');
  need(tx.from_address.toLowerCase()===manifest.sender.toLowerCase()&&tx.to_address.toLowerCase()===manifest.address.toLowerCase(),step+':PARTIES');
  if(step!=='deployment'){
    const journal=load('evidence/'+step+'.json');
    const call=clean((abi.calldata??abi).decode(new Uint8Array(Buffer.from(tx.data.calldata.base64,'base64'))));
    need(call.method===journal.functionName&&equal(call.args,journal.args),step+':CALLDATA_MISMATCH');
  }
  console.log(step+': FINALIZED / MAJORITY_AGREE / return / full consensus');
}
const b=JSON.parse(await client.readContract({address:manifest.address,functionName:'get_book',args:[manifest.book_id],transactionHashVariant:TransactionHashVariant.LATEST_FINAL}));
need(b.state==='FROZEN'&&b.revision===4,'FINAL_STATE');
need(b.id===manifest.book_id&&b.owner===manifest.sender.toLowerCase(),'BOOK_ID');
need(b.product===fixture.product&&equal(b.units,fixture.units),'FROZEN_SCOPE');
need(b.scope_hash===hash({version:'ratiorail-1',product:b.product,units:b.units}),'SCOPE_HASH');
need(b.attempts.length===3&&b.edges.length===2,'ATTEMPT_OR_EDGE_COUNT');
for(let i=0;i<3;i++){
  const a=b.attempts[i], f=fixture.links[i];
  need(a.from===f.source&&a.to===f.target&&a.statement===f.statement&&a.outcome===f.expected,'FIXTURE_'+i);
  need(a.decision.status==='EXACT'&&equal(a.decision.ratio,f.ratio),'DECISION_'+i);
  need(a.input_hash===hash({scope_hash:b.scope_hash,source:a.from,target:a.to,statement:a.statement}),'INPUT_HASH_'+i);
}
need(equal(b.edges,[{attempt:0,from:0,to:1,ratio:[6,1]},{attempt:1,from:1,to:2,ratio:[4,1]}]),'ACTIVE_FOREST');
const witness=b.attempts[2].witness;
need(equal(witness.cycle_product,[5,6])&&equal(witness.existing_path.ratio,[24,1]),'CONFLICT_RATIO');
need(equal(witness.existing_path.steps,[{attempt:0,reverse:false},{attempt:1,reverse:false}]),'CONFLICT_PATH');
const expectedTable=[[[1,1],[6,1],[24,1]],[[1,6],[1,1],[4,1]],[[1,24],[1,4],[1,1]]];
need(equal(b.table,expectedTable),'TABLE');
need(b.table_hash===hash({scope_hash:b.scope_hash,table:b.table}),'TABLE_HASH');
const f=fixture.conversion;
const conversion=JSON.parse(await client.readContract({address:manifest.address,functionName:'convert',args:[manifest.book_id,f.source,f.target,f.amount],transactionHashVariant:TransactionHashVariant.LATEST_FINAL}));
for(const k of ['numerator','denominator','whole_units','remainder_numerator'])need(conversion[k]===f[k],'CONVERSION_'+k);
need(conversion.table_hash===b.table_hash,'CONVERSION_HASH');
console.log('Verified deployed source, exact calldata, frozen scope, accepted forest, conflict witness, table hash and 25/24 conversion.');
process.exit(0);
