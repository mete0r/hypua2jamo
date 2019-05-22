[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmete0r%2Fhypua2jamo.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fmete0r%2Fhypua2jamo?ref=badge_shield)

hypua2jamo
==========

Convert `Hanyang-PUA code <https://ko.wikipedia.org/wiki/%EC%98%9B%ED%95%9C%EA%B8%80#%ED%95%9C%EC%96%91_%EC%82%AC%EC%9A%A9%EC%9E%90_%EC%A0%95%EC%9D%98_%EC%98%81%EC%97%AD_%EC%BD%94%EB%93%9C>`_ (U+E0BC~U+F8F7) to unicode Hangul Jamo (U+1100~U+11FF), i.e. `Syllable-Initial-Peak-Final Encoding (첫가끝 코드) <https://ko.wikipedia.org/wiki/%EC%98%9B%ED%95%9C%EA%B8%80#%EC%B2%AB%EA%B0%80%EB%81%9D_%EC%BD%94%EB%93%9C>`_.

Example
-------

   >>> from hypua2jamo import translate
   >>> pua = u'\ub098\ub78f\u302e\ub9d0\u302f\uebd4\ubbf8\u302e'
   >>> translate(pua)
   u'\ub098\ub78f\u302e\ub9d0\u302f\u110a\u119e\ubbf8\u302e'
   >>> print _
   나랏말ᄊ미
   >>> translate(pua, composed=False)
   u'\ub098\ub78f\u302e\ub9d0\u302f\u1109\u1109\u119e\ubbf8\u302e'
   >>> print _
   나랏말ㅅㅅ미

Installation
------------

from `pypi <http://pypi.python.org/pypi/hypua2jamo>`_::

   pip install hypua2jamo

from `github <https://github.com/mete0r/hypua2jamo>`_::

   git clone git://github.com/mete0r/hypua2jamo.git
   cd hypua2jamo
   python bootstrap.py
   bin/buildout
   python data2py.py

Requirements
------------

- Python 2.7, Python 3.4

Documentation & Development
---------------------------

- Documentation: `http://hypua2jamo.readthedocs.org <http://hypua2jamo.readthedocs.org>`_
- GitHub: `https://github.com/mete0r/hypua2jamo <https://github.com/mete0r/hypua2jamo>`_
- Issue tracker: `https://github.com/mete0r/hypua2jamo/issues <https://github.com/mete0r/hypua2jamo/issues>`_
- Bug reports, feedbacks and contributions are welcome!

Contributors
------------

Maintainer: `mete0r <https://github.com/mete0r>`_

License
-------

.. image:: http://www.gnu.org/graphics/lgplv3-147x51.png
   :width: 147px

`GNU Lesser General Public License Version 3 <http://www.gnu.org/licenses/lgpl.html>`_
`(text version) <http://www.gnu.org/licenses/lgpl-3.0.txt>`_

Disclosure
----------

This work is based on `KTUG <http://www.ktug.or.kr>`_
`Hanyang PUA Table Project <http://faq.ktug.or.kr/faq/HanyangPuaTableProject>`_.


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmete0r%2Fhypua2jamo.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fmete0r%2Fhypua2jamo?ref=badge_large)