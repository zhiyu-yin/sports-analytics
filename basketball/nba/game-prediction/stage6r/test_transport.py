import unittest,json,socket,ssl,sys,io
from unittest.mock import patch
from pathlib import Path
import support as s
class TransportTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.proof,cls.cap=s.launch('local_tls');s.old.durable(s.E/'local_tls_proof.json',cls.proof)
 def test_A_real_ssl_construction(self):self.assertTrue(self.proof.get('real_tls_handshake'),self.proof);self.assertTrue(self.proof['certificate_verified'])
 def test_B_normal_development_block(self):
  with self.assertRaises(RuntimeError):socket.socket()
 def test_C_missing_capability_rejected(self):
  result,_=s.launch('local_tls',request={});self.assertFalse(result['passed'])
 def test_D_no_stale_inheritance(self):self.assertTrue(self.proof.get('ssl_base_is_original_socket'),self.proof);self.assertFalse(any('BlockedSocket' in v for v in self.proof['ssl_mro']))
 def test_E_revocation(self):self.assertTrue(self.proof.get('revocation_blocks_socket'),self.proof)
 def test_F_https_through_real_tls(self):self.assertTrue(self.proof.get('https_fixture'),self.proof);self.assertEqual(self.proof['response_status'],200)
 def test_G_consumed_capability_rejected(self):
  result,_=s.launch('local_tls',request=self.cap);self.assertFalse(result['passed']);self.assertEqual(result['error_type'],'FileExistsError')
 def test_H_no_final_data_in_preflight(self):
  self.assertFalse(self.proof['final_data_access']);self.assertTrue(self.proof['part_a_final_endpoint_rejected']);self.assertTrue(all(row[0]=='localhost' for row in self.proof['dns_calls']))
 def test_wrong_nonce_rejected(self):
  result,_=s.launch('local_tls',request=dict(self.cap,nonce='wrong'));self.assertFalse(result['passed'])
 def test_part_b_requires_gate_and_ledger(self):
  with self.assertRaises(FileNotFoundError):s.launch('part_b')
 def test_root_cause_without_network(self):
  blocked=socket.socket;original=blocked.__mro__[1]
  self.assertIn(blocked,ssl.SSLSocket.__mro__)
  failures=[]
  for local_replacement in [False,True]:
   raw=original()
   try:
    with patch.object(socket,'socket',original if local_replacement else blocked):
     ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
     with self.assertRaisesRegex(RuntimeError,'Development network blocked'):
      ctx.wrap_socket(raw,server_hostname='localhost',do_handshake_on_connect=False)
    failures.append(dict(local_socket_replaced=local_replacement,tls_construction='Development network blocked'))
   finally:raw.close()
  s.old.durable(s.E/'tls_root_cause.json',dict(reproduced=True,ssl_mro=[c.__module__+'.'+c.__qualname__ for c in ssl.SSLSocket.__mro__],blocked_socket_id=id(blocked),ssl_base_id=id(ssl.SSLSocket.__mro__[1]),base_is_blocked=ssl.SSLSocket.__mro__[1] is blocked,original_socket_id=id(original),attempts=failures,network_connect_calls=0,explanation='Startup pth imports nba_game_prediction and installs BlockedSocket before ssl imports socket as its class base. Later socket.socket rebinding cannot change SSLSocket.__mro__.'))
